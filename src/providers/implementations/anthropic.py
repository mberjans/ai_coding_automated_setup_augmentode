"""Anthropic provider implementation for the LLM API."""
import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Union, cast

import httpx
from typing_extensions import TypedDict
import os

from src.providers.interface import (
    AuthError,
    ProviderError,
    RateLimitError,
    TransientError,
    PermanentError,
    is_valid_client,
    require_client,
)

# Set up logging
logger = logging.getLogger(__name__)

# Type aliases
Message = Dict[str, str]
MessageList = List[Message]


class AnthropicProvider:
    """Provider for the Anthropic API."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Anthropic provider with the given configuration.
        
        Args:
            config: Configuration dictionary containing:
                - api_key: Anthropic API key (required unless api_key_env is provided)
                - api_key_env: Environment variable name containing the API key (optional alternative to api_key)
                - model: Model name (e.g., "claude-3-opus-20240229") (required)
                - max_tokens: Maximum number of tokens to generate (default: 4096)
                - temperature: Sampling temperature (default: 0.7)
                - top_p: Nucleus sampling parameter (default: 0.9)
                - top_k: Top-k sampling parameter (default: 5)
                - stop_sequences: List of stop sequences (default: ["\n\nHuman:"])
                - timeout: Request timeout in seconds (default: 30.0)
                - max_retries: Maximum number of retries for failed requests (default: 3)
        """
        # Resolve API key from direct value or environment variable name
        api_key_value = config.get("api_key")
        if not api_key_value:
            api_key_env = config.get("api_key_env")
            if api_key_env:
                if api_key_env in os.environ:
                    api_key_value = os.environ.get(api_key_env)
                else:
                    raise ValueError("api_key_env provided but environment variable is not set")
            else:
                raise ValueError("api_key is required in the configuration")
        self.api_key = api_key_value
        self.model = self._get_required_config(config, "model")
        
        # Optional parameters with defaults
        self.max_tokens = config.get("max_tokens", 4096)
        self.temperature = config.get("temperature", 0.7)
        self.top_p = config.get("top_p", 0.9)
        self.top_k = config.get("top_k", 5)
        self.stop_sequences = config.get("stop_sequences", ["\n\nHuman:"])
        self.timeout = config.get("timeout", 30.0)
        self.max_retries = config.get("max_retries", 3)
        
        # HTTP client
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout, connect=10.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )
        
        # Base URL for the Anthropic API
        self.base_url = "https://api.anthropic.com/v1"
    
    def _get_required_config(self, config: Dict[str, Any], key: str) -> Any:
        """Get a required configuration value or raise an error if missing."""
        value = config.get(key)
        if value is None:
            raise ValueError(f"{key} is required in the configuration")
        return value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the provider configuration to a dictionary."""
        return {
            "api_key": self.api_key,
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "stop_sequences": self.stop_sequences,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
        }
    
    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'AnthropicProvider':
        """Create a provider instance from a configuration dictionary."""
        return cls(config)
    
    async def prepare_prompt(
        self, 
        prompt_bundle: Dict[str, str],
        processed_docs: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Prepare a prompt for the Anthropic API.
        
        Args:
            prompt_bundle: Dictionary containing prompt templates for different tasks.
                Should contain keys like "plan", "tickets", "checklist", etc.
            processed_docs: List of processed documents to include in the prompt.
                Each document should be a dictionary with at least a "text" key.
                
        Returns:
            A JSON string containing the prepared prompt and metadata.
        """
        # Build the system prompt
        system_prompt = (
            "You are an expert software developer working on a coding project. "
            "Your task is to help plan, break down, and implement features based on the requirements. "
            "Be concise, precise, and follow best practices."
        )
        
        # Build the user prompt from the prompt bundle
        user_prompt_parts = []
        
        # Add document content if provided
        if processed_docs:
            docs_section = "## Context\n\n"
            for i, doc in enumerate(processed_docs, 1):
                doc_text = doc.get("text", "").strip()
                if doc_text:
                    source = doc.get("metadata", {}).get("source", f"document_{i}")
                    docs_section += f"### {source}\n{doc_text}\n\n"
            
            if docs_section.strip():
                user_prompt_parts.append(docs_section.strip())
        
        # Add the main task prompts
        for key, prompt in prompt_bundle.items():
            if prompt and prompt.strip():
                user_prompt_parts.append(f"## {key.capitalize()}\n\n{prompt}")
        
        # Combine all parts
        user_prompt = "\n\n".join(user_prompt_parts)
        
        # Prepare the messages for the API
        messages = [
            {"role": "user", "content": user_prompt}
        ]
        
        # Return a JSON string with the prepared prompt and metadata
        return json.dumps({
            "prompt": user_prompt,
            "messages": messages,
            "system": system_prompt,
            **prompt_bundle  # Include all prompt templates in the output
        })
    
    async def call(self, prepared_prompt: str) -> Dict[str, Any]:
        """Call the Anthropic API with the prepared prompt.
        
        Args:
            prepared_prompt: JSON string containing the prepared prompt and metadata.
                This should be the output of the prepare_prompt method.
                
        Returns:
            A dictionary containing the API response with keys:
                - content: The generated text response
                - usage: Token usage information
                - model: The model used
                - stop_reason: The reason the generation stopped
        
        Raises:
            AuthError: If authentication fails (invalid API key)
            RateLimitError: If rate limited
            TransientError: For temporary failures (network issues, server errors)
            PermanentError: For permanent failures (invalid requests, etc.)
            ProviderError: For other unexpected errors
        """
        try:
            # Parse the prepared prompt
            try:
                prompt_data = json.loads(prepared_prompt)
                messages = prompt_data.get("messages", [])
                system = prompt_data.get("system", "")
            except json.JSONDecodeError as e:
                raise PermanentError(f"Invalid prepared prompt: {e}")
            
            # Prepare the request payload
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "top_k": self.top_k,
                "stop_sequences": self.stop_sequences,
            }
            
            if system:
                payload["system"] = system
            
            # Headers
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            
            # Make the API request with retries
            response = await self._make_request_with_retries(
                "POST",
                f"{self.base_url}/messages",
                json=payload,
                headers=headers,
            )
            
            # Extract the response content
            response_data = response.json()
            
            # Format the response
            content = ""
            if "content" in response_data:
                for content_block in response_data["content"]:
                    if content_block["type"] == "text":
                        content += content_block["text"]
            
            return {
                "content": content,
                "usage": {
                    "input_tokens": response_data.get("usage", {}).get("input_tokens", 0),
                    "output_tokens": response_data.get("usage", {}).get("output_tokens", 0),
                    "total_tokens": response_data.get("usage", {}).get("total_tokens", 0),
                },
                "model": response_data.get("model", self.model),
                "stop_reason": response_data.get("stop_reason", "unknown"),
            }
            
        except Exception as e:
            # Re-raise known error types
            if isinstance(e, (AuthError, RateLimitError, TransientError, PermanentError, ProviderError)):
                raise
            
            # Wrap other exceptions in ProviderError
            raise ProviderError(f"Error calling Anthropic API: {e}") from e
    
    async def _make_request_with_retries(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """Make an HTTP request with retries for transient failures."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.request(method, url, **kwargs)
                
                # Check for errors
                if response.status_code == 401:
                    raise AuthError("Authentication failed: Invalid API key")
                elif response.status_code == 429:
                    retry_after = float(response.headers.get("retry-after", 1.0))
                    if attempt < self.max_retries:
                        logger.warning(
                            f"Rate limited. Retrying after {retry_after} seconds (attempt {attempt + 1}/{self.max_retries})"
                        )
                        await asyncio.sleep(retry_after)
                        continue
                    raise RateLimitError(f"Rate limited. Retry after {retry_after} seconds")
                elif response.status_code >= 500:
                    if attempt < self.max_retries:
                        delay = min(2 ** attempt, 60)  # Exponential backoff, max 60s
                        logger.warning(
                            f"Server error {response.status_code}. Retrying in {delay}s (attempt {attempt + 1}/{self.max_retries})"
                        )
                        await asyncio.sleep(delay)
                        continue
                    raise TransientError(f"Server error: {response.status_code}")
                elif response.status_code >= 400:
                    error_data = response.json().get("error", {})
                    error_msg = error_data.get("message", f"Bad request: {response.status_code}")
                    raise PermanentError(error_msg)
                
                # Request was successful
                return response
                
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                last_exception = e
                if attempt == self.max_retries:
                    break
                    
                # For network errors, use exponential backoff
                delay = min(2 ** attempt, 60)  # Exponential backoff, max 60s
                logger.warning(
                    f"Request failed (attempt {attempt + 1}/{self.max_retries + 1}). "
                    f"Retrying in {delay}s... Error: {str(e)}"
                )
                await asyncio.sleep(delay)
        
        # If we've exhausted all retries, raise the last exception
        if isinstance(last_exception, httpx.HTTPStatusError):
            if last_exception.response.status_code == 429:
                raise RateLimitError(f"Rate limit exceeded after {self.max_retries + 1} attempts") from last_exception
            elif last_exception.response.status_code >= 500:
                raise TransientError(f"Server error after {self.max_retries + 1} attempts") from last_exception
            else:
                raise PermanentError(f"Request failed after {self.max_retries + 1} attempts") from last_exception
        else:
            raise TransientError(f"Request failed after {self.max_retries + 1} attempts") from last_exception

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    def __del__(self):
        """Ensure resources are cleaned up when the object is garbage collected."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.close())
            else:
                loop.run_until_complete(self.close())
        except Exception:
            pass  # Ignore errors during cleanup


# Register the provider with the registry
# This allows the provider to be created by name
_PROVIDER_CLASS = AnthropicProvider

# Export the provider class and factory function
__all__ = ["AnthropicProvider"]
