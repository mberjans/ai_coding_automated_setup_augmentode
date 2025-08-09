"""OpenRouter provider implementation."""
import json
import logging
import time
import asyncio
import httpx
from typing import Dict, Any, Optional

from ..interface import ProviderError, AuthError, RateLimitError, TransientError

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30.0  # seconds
DEFAULT_MAX_RETRIES = 3

class OpenRouterProvider:
    """Provider for OpenRouter API."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the OpenRouter provider.
        
        Args:
            config: Configuration dictionary with the following keys:
                - api_key: OpenRouter API key (required)
                - model: Model to use (e.g., "openai/gpt-4-turbo") (required)
                - max_tokens: Maximum tokens to generate (default: 4096)
                - temperature: Sampling temperature (default: 0.7)
                - top_p: Nucleus sampling parameter (default: 1.0)
                - headers: Additional headers to include in requests
                - timeout: Request timeout in seconds (default: 30.0)
                - max_retries: Maximum number of retries for failed requests (default: 3)
        """
        # Required parameters
        self.api_key = config.get("api_key")
        self.model = config.get("model")
        
        if not self.api_key:
            raise ValueError("api_key is required")
        if not self.model:
            raise ValueError("model is required")
        
        # Optional parameters with defaults
        self.max_tokens = config.get("max_tokens", 4096)
        self.temperature = config.get("temperature", 0.7)
        self.top_p = config.get("top_p", 1.0)
        self.timeout = float(config.get("timeout", DEFAULT_TIMEOUT))
        self.max_retries = int(config.get("max_retries", DEFAULT_MAX_RETRIES))
        
        # Headers
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            **(config.get("headers") or {})
        }
        
        # Initialize HTTP client
        self._client = None
    
    async def prepare_prompt(
        self,
        prompt_bundle: Dict[str, str],
        processed_docs: Optional[list] = None
    ) -> str:
        """Prepare the prompt for the OpenRouter API.
        
        Args:
            prompt_bundle: Dictionary with prompt sections (plan, tickets, checklist)
            processed_docs: List of processed documents with text and metadata
            
        Returns:
            JSON string containing the prepared prompt
        """
        # Combine document texts if provided
        doc_texts = []
        if processed_docs:
            for doc in processed_docs:
                if isinstance(doc, dict) and "text" in doc:
                    doc_texts.append(doc["text"])
        
        # Create system message with instructions
        system_prompt = (
            "You are an AI assistant helping to generate project documentation. "
            "Follow the instructions carefully and provide detailed, structured output."
        )
        
        # Create user message with the prompt bundle
        user_message = "\n\n".join(
            f"## {key.upper()}\n{value}" 
            for key, value in prompt_bundle.items() 
            if value
        )
        
        # Add document context if available
        if doc_texts:
            docs_section = "## DOCUMENTS\n" + "\n\n---\n\n".join(doc_texts)
            user_message = f"{user_message}\n\n{docs_section}"
        
        # Prepare messages for the API
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # Return as JSON string
        return json.dumps({
            "prompt": user_message,
            **prompt_bundle,
            "messages": messages,
            "system": system_prompt
        })
    
    async def call(self, prepared_prompt: str) -> Dict[str, Any]:
        """Call the OpenRouter API with the prepared prompt.
        
        Args:
            prepared_prompt: JSON string from prepare_prompt
            
        Returns:
            Dictionary with the response content and metadata
            
        Raises:
            AuthError: If authentication fails
            RateLimitError: If rate limited
            TransientError: For temporary failures
            ProviderError: For other errors
        """
        try:
            prompt_data = json.loads(prepared_prompt)
        except json.JSONDecodeError as e:
            raise ProviderError(f"Invalid prepared prompt: {e}")
        
        # Extract messages from prepared prompt
        messages = prompt_data.get("messages", [])
        if not messages:
            messages = [{"role": "user", "content": prompt_data.get("prompt", "")}]
        
        # Prepare request data
        request_data = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
        }
        
        # Make the request with retries
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(
                    timeout=httpx.Timeout(self.timeout, connect=10.0),
                    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
                ) as client:
                    response = await client.request(
                        "POST",
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=self.headers,
                        json=request_data
                    )
                    
                    # Check for errors
                    if response.status_code == 401:
                        raise AuthError("Invalid API key")
                    elif response.status_code == 429:
                        retry_after = float(response.headers.get("retry-after", 1.0))
                        if attempt < self.max_retries:
                            logger.warning(
                                "Rate limited, retrying after %.1f seconds (attempt %d/%d)",
                                retry_after, attempt + 1, self.max_retries
                            )
                            await asyncio.sleep(retry_after)
                            continue
                        raise RateLimitError("Rate limit exceeded")
                    elif response.status_code >= 500:
                        if attempt < self.max_retries:
                            logger.warning(
                                "Server error, retrying (attempt %d/%d)",
                                attempt + 1, self.max_retries
                            )
                            await asyncio.sleep(min(2 ** attempt, 10))  # Exponential backoff
                            continue
                        raise TransientError(f"Server error: {response.status_code}")
                    elif response.status_code != 200:
                        error_data = response.json()
                        error_msg = error_data.get("error", {}).get("message", "Unknown error")
                        raise ProviderError(f"API error: {error_msg}")
                    
                    # Parse successful response
                    result = response.json()
                    choice = result["choices"][0]
                    
                    return {
                        "content": choice["message"]["content"],
                        "usage": result.get("usage", {}),
                        "model": self.model,
                        "provider": "openrouter"
                    }
                    
            except httpx.HTTPError as e:
                last_exception = e
                if attempt < self.max_retries:
                    logger.warning("Network error, retrying (attempt %d/%d)", attempt + 1, self.max_retries)
                    await asyncio.sleep(min(2 ** attempt, 10))  # Exponential backoff
                    continue
                raise TransientError(f"Network error: {e}")
        
        # If we get here, all retries were exhausted
        if last_exception:
            raise TransientError(f"Failed after {self.max_retries} attempts: {last_exception}")
        raise ProviderError("Failed to complete request")
    
    async def close(self):
        """Close any resources held by the provider."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    def __del__(self):
        """Ensure resources are cleaned up when the object is destroyed."""
        if self._client:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.close())
                else:
                    loop.run_until_complete(self.close())
            except Exception:
                pass  # Best effort cleanup


# Functional interface for compatibility with the provider system
def create_provider(config: Dict[str, Any]) -> dict:
    """Create a functional provider interface.
    
    Args:
        config: Provider configuration
        
    Returns:
        Dictionary with callable methods
    """
    provider = OpenRouterProvider(config)
    
    async def _prepare_prompt(prompt_bundle: Dict[str, str], processed_docs=None):
        return await provider.prepare_prompt(prompt_bundle, processed_docs)
    
    async def _call(prepared_prompt: str):
        return await provider.call(prepared_prompt)
    
    async def _close():
        await provider.close()
    
    return {
        "prepare_prompt": _prepare_prompt,
        "call": _call,
        "close": _close,
        "__provider__": provider  # Keep reference to the provider instance
    }
