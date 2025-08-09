"""Tests for the Anthropic provider adapter."""
import json
import os
import tempfile
from unittest.mock import MagicMock, patch, ANY, AsyncMock
import pytest
import pytest_asyncio
import httpx

# Enable asyncio mode for all tests in this module
pytestmark = pytest.mark.asyncio

from src.providers.interface import ProviderError, RateLimitError, TransientError

# Skip this test module if ANTHROPIC_API_KEY is not set
pytestmark = pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY environment variable not set"
)

# Sample configuration for tests
SAMPLE_CONFIG = {
    "api_key": "test-api-key",
    "model": "claude-3-opus-20240229",
    "max_tokens": 1000,
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 5,
    "stop_sequences": ["\n\nHuman:"],
    "timeout": 30.0,
    "max_retries": 3
}

# Sample prompt bundle for tests
SAMPLE_PROMPT_BUNDLE = {
    "plan": "Test plan prompt",
    "tickets": "Test tickets prompt",
    "checklist": "Test checklist prompt"
}

# Sample processed documents for tests
SAMPLE_PROCESSED_DOCS = [
    {"text": "Document 1 content", "metadata": {"source": "doc1.txt"}},
    {"text": "Document 2 content", "metadata": {"source": "doc2.txt"}}
]

# Sample successful response from Anthropic API
SAMPLE_API_RESPONSE = {
    "id": "msg_123",
    "type": "message",
    "role": "assistant",
    "content": [
        {"type": "text", "text": "Test response"}
    ],
    "model": "claude-3-opus-20240229",
    "stop_reason": "end_turn",
    "stop_sequence": None,
    "usage": {
        "input_tokens": 10,
        "output_tokens": 20,
        "total_tokens": 30
    }
}


def test_anthropic_provider_initialization():
    """Test that AnthropicProvider can be initialized with valid config."""
    from src.providers.implementations.anthropic import AnthropicProvider
    
    # Test with minimal required config
    provider = AnthropicProvider({"api_key": "test-key", "model": "claude-3-opus-20240229"})
    assert provider.model == "claude-3-opus-20240229"
    assert provider.max_tokens == 4096  # Default value
    
    # Test with full config
    provider = AnthropicProvider(SAMPLE_CONFIG)
    assert provider.api_key == "test-api-key"
    assert provider.model == "claude-3-opus-20240229"
    assert provider.max_tokens == 1000
    assert provider.temperature == 0.7
    assert provider.top_p == 0.9
    assert provider.top_k == 5
    assert provider.stop_sequences == ["\n\nHuman:"]
    assert provider.timeout == 30.0
    assert provider.max_retries == 3


def test_anthropic_provider_missing_required_fields():
    """Test that initialization fails with missing required fields."""
    from src.providers.implementations.anthropic import AnthropicProvider
    
    # Missing api_key
    with pytest.raises(ValueError, match="api_key is required"):
        AnthropicProvider({"model": "claude-3-opus-20240229"})
    
    # Missing model
    with pytest.raises(ValueError, match="model is required"):
        AnthropicProvider({"api_key": "test-key"})


@pytest.mark.asyncio
async def test_anthropic_provider_prepare_prompt():
    """Test that prepare_prompt formats the prompt correctly."""
    from src.providers.implementations.anthropic import AnthropicProvider
    
    # Create provider and call prepare_prompt
    provider = AnthropicProvider(SAMPLE_CONFIG)
    result = await provider.prepare_prompt(
        prompt_bundle=SAMPLE_PROMPT_BUNDLE,
        processed_docs=SAMPLE_PROCESSED_DOCS
    )
    
    # Verify the result is a string (JSON string)
    assert isinstance(result, str)
    prompt_data = json.loads(result)
    
    # Verify the expected keys are present
    assert "prompt" in prompt_data
    assert "plan" in prompt_data
    assert "tickets" in prompt_data
    assert "checklist" in prompt_data
    assert "messages" in prompt_data
    assert "system" in prompt_data
    
    # Verify the prompt includes the document content
    for doc in SAMPLE_PROCESSED_DOCS:
        assert doc["text"] in prompt_data["prompt"]
    
    # Verify the messages include the user content
    messages = prompt_data["messages"]
    assert len(messages) == 1  # Single user message
    assert messages[0]["role"] == "user"
    assert SAMPLE_PROMPT_BUNDLE["plan"] in messages[0]["content"]
    
    # Verify the system prompt is included
    assert isinstance(prompt_data["system"], str)
    assert len(prompt_data["system"]) > 0


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_anthropic_provider_call_success(mock_client_class):
    """Test successful call to the Anthropic API."""
    from src.providers.implementations.anthropic import AnthropicProvider
    
    # Create a mock response with proper attributes
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = SAMPLE_API_RESPONSE
    
    # Create a mock client instance with proper request method
    mock_client = AsyncMock()
    mock_client.request = AsyncMock(return_value=mock_response)
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    
    # Configure the client class to return our mock client
    mock_client_class.return_value = mock_client
    
    # Create provider and call prepare_prompt
    provider = AnthropicProvider(SAMPLE_CONFIG)
    prepared_prompt = json.dumps({
        "prompt": "Test prompt",
        "plan": "Test plan",
        "tickets": "Test tickets",
        "checklist": "Test checklist",
        "messages": [{"role": "user", "content": "Test prompt"}],
        "system": "Test system prompt"
    })
    
    # Call the method under test
    result = await provider.call(prepared_prompt)
    
    # Verify the result contains the expected fields
    assert "content" in result
    assert "usage" in result
    assert result["content"] == "Test response"
    assert result["usage"]["total_tokens"] == 30
    
    # Verify the client was called with the correct parameters
    mock_client_class.assert_called_once_with(
        timeout=httpx.Timeout(30.0, connect=10.0),
        limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
    )
    
    # Verify the request was made with the correct parameters
    mock_client.request.assert_awaited_once_with(
        "POST",
        "https://api.anthropic.com/v1/messages",
        json={
            "model": "claude-3-opus-20240229",
            "messages": [{"role": "user", "content": "Test prompt"}],
            "max_tokens": 1000,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 5,
            "stop_sequences": ["\n\nHuman:"],
            "system": "Test system prompt"
        },
        headers={
            "x-api-key": "test-api-key",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    )


@pytest.mark.asyncio
@patch('asyncio.sleep')
@patch('httpx.AsyncClient')
async def test_anthropic_provider_rate_limit_retry(mock_client_class, mock_sleep):
    """Test that the provider retries on rate limit errors (429)."""
    from src.providers.implementations.anthropic import AnthropicProvider
    
    # Create a successful mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = SAMPLE_API_RESPONSE
    mock_response.headers = {}
    
    # Create a mock client that returns the successful response after rate limit
    mock_client = AsyncMock()
    
    # First call raises RateLimitError, second call succeeds
    async def mock_request(*args, **kwargs):
        if not hasattr(mock_request, '_call_count'):
            mock_request._call_count = 1
            # First call raises RateLimitError
            mock_rate_limit_response = MagicMock()
            mock_rate_limit_response.status_code = 429
            mock_rate_limit_response.headers = {"retry-after": "1"}
            mock_rate_limit_response.json.return_value = {"error": {"type": "rate_limit_error"}}
            mock_rate_limit_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Rate limited",
                request=MagicMock(),
                response=mock_rate_limit_response
            )
            return mock_rate_limit_response
        else:
            # Second call returns success
            return mock_response
    
    mock_client.request = AsyncMock(side_effect=mock_request)
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    
    # Configure the client class to return our mock client
    mock_client_class.return_value = mock_client
    
    # Create provider with max_retries=1
    provider = AnthropicProvider({
        **SAMPLE_CONFIG,
        "max_retries": 1,  # Set max_retries to 1 for this test
        "retry_delay": 0.1  # Shorter delay for testing
    })
    
    prepared_prompt = json.dumps({
        "prompt": "Test prompt",
        "messages": [{"role": "user", "content": "Test prompt"}],
        "system": "Test system"
    })
    
    # Call should succeed after retry
    result = await provider.call(prepared_prompt)
    
    # Should have retried once (2 calls total)
    assert mock_client.request.await_count == 2
    
    # Should have slept with the retry-after delay
    mock_sleep.assert_called_once_with(1.0)  # From retry-after header
    
    # Should return the successful response
    assert result["content"] == "Test response"
    
    # Verify the request was made with the correct parameters
    expected_call = {
        "model": "claude-3-opus-20240229",
        "messages": [{"role": "user", "content": "Test prompt"}],
        "system": "Test system",
        "max_tokens": 1000,
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 5,
        "stop_sequences": ["\n\nHuman:"]
    }
    
    # Check both calls had the same parameters
    for call in mock_client.request.await_args_list:
        args, kwargs = call
        assert args[0] == "POST"
        assert args[1] == "https://api.anthropic.com/v1/messages"
        assert kwargs["json"] == expected_call


@pytest.mark.asyncio
@patch('asyncio.sleep')
@patch('httpx.AsyncClient')
async def test_anthropic_provider_server_error_retry(mock_client_class, mock_sleep):
    """Test that the provider retries on server errors (5xx)."""
    from src.providers.implementations.anthropic import AnthropicProvider
    
    # Create a successful mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = SAMPLE_API_RESPONSE
    mock_response.headers = {}
    
    # Create a mock client that returns the successful response after a server error
    mock_client = AsyncMock()
    
    # First call raises 500 error, second call succeeds
    async def mock_request(*args, **kwargs):
        if not hasattr(mock_request, '_call_count'):
            mock_request._call_count = 1
            # First call raises 500 error
            mock_error_response = MagicMock()
            mock_error_response.status_code = 500
            mock_error_response.headers = {}
            mock_error_response.json.return_value = {"error": {"type": "internal_server_error"}}
            return mock_error_response
        else:
            # Second call returns success
            return mock_response
    
    mock_client.request = AsyncMock(side_effect=mock_request)
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    
    # Configure the client class to return our mock client
    mock_client_class.return_value = mock_client
    
    # Create provider with max_retries=1
    provider = AnthropicProvider({
        **SAMPLE_CONFIG,
        "max_retries": 1,  # Set max_retries to 1 for this test
        "retry_delay": 0.1  # Shorter delay for testing
    })
    
    prepared_prompt = json.dumps({
        "prompt": "Test prompt",
        "messages": [{"role": "user", "content": "Test prompt"}],
        "system": "Test system"
    })
    
    # Call should succeed after retry
    result = await provider.call(prepared_prompt)
    
    # Should have retried once (2 calls total)
    assert mock_client.request.await_count == 2
    
    # Should have slept with the retry delay
    mock_sleep.assert_called_once()
    
    # Should return the successful response
    assert result["content"] == "Test response"


@pytest.mark.asyncio
@patch('asyncio.sleep')
@patch('httpx.AsyncClient')
async def test_anthropic_provider_max_retries_exceeded(mock_client_class, mock_sleep):
    """Test that the provider raises an exception after max retries."""
    from src.providers.implementations.anthropic import AnthropicProvider
    from src.providers.interface import RateLimitError
    
    # Create a mock client that always returns 429 (rate limit)
    mock_client = AsyncMock()
    
    # Create a mock response for rate limit
    mock_rate_limit_response = MagicMock()
    mock_rate_limit_response.status_code = 429
    mock_rate_limit_response.headers = {"retry-after": "1"}
    mock_rate_limit_response.json.return_value = {"error": {"type": "rate_limit_error"}}
    mock_rate_limit_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Rate limited",
        request=MagicMock(),
        response=mock_rate_limit_response
    )
    
    # Always return rate limit response
    mock_client.request = AsyncMock(return_value=mock_rate_limit_response)
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    
    # Configure the client class to return our mock client
    mock_client_class.return_value = mock_client
    
    # Create provider with only 1 retry
    provider = AnthropicProvider({
        **SAMPLE_CONFIG,
        "max_retries": 1,  # Only 1 retry for this test
        "retry_delay": 0.1  # Shorter delay for testing
    })
    
    prepared_prompt = json.dumps({
        "prompt": "Test prompt",
        "messages": [{"role": "user", "content": "Test prompt"}],
        "system": "Test system"
    })
    
    # Verify the call raises RateLimitError
    with pytest.raises(RateLimitError):
        await provider.call(prepared_prompt)
    
    # Should have made 2 attempts (initial + 1 retry)
    assert mock_client.request.await_count == 2
    
    # Should have slept once (for the retry)
    assert mock_sleep.await_count == 1


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_anthropic_provider_invalid_api_key(mock_client_class):
    """Test that the provider raises an exception for invalid API key."""
    from src.providers.implementations.anthropic import AnthropicProvider
    from src.providers.interface import AuthError
    
    # Create a mock client that returns 401 (unauthorized)
    mock_client = AsyncMock()
    
    # Create a mock response for invalid API key
    mock_auth_error_response = MagicMock()
    mock_auth_error_response.status_code = 401
    mock_auth_error_response.json.return_value = {"error": {"type": "authentication_error"}}
    mock_auth_error_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Unauthorized",
        request=MagicMock(),
        response=mock_auth_error_response
    )
    
    # Configure the client to return the auth error response
    mock_client.request = AsyncMock(return_value=mock_auth_error_response)
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    
    # Configure the client class to return our mock client
    mock_client_class.return_value = mock_client
    
    # Create provider
    provider = AnthropicProvider(SAMPLE_CONFIG)
    
    prepared_prompt = json.dumps({
        "prompt": "Test prompt",
        "messages": [{"role": "user", "content": "Test prompt"}],
        "system": "Test system"
    })
    
    # Verify the call raises AuthError
    with pytest.raises(AuthError):
        await provider.call(prepared_prompt)
    
    # Should have made exactly 1 attempt (no retries for auth errors)
    assert mock_client.request.await_count == 1


@pytest.mark.asyncio
@patch('asyncio.sleep')
@patch('httpx.AsyncClient')
async def test_anthropic_provider_network_error(mock_client_class, mock_sleep):
    """Test that the provider handles network errors."""
    from src.providers.implementations.anthropic import AnthropicProvider
    from src.providers.interface import TransientError
    
    # Create a mock client that raises a network error
    mock_client = AsyncMock()
    
    # Configure the client to raise a network error
    mock_client.request = AsyncMock(side_effect=httpx.RequestError("Network error"))
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    
    # Configure the client class to return our mock client
    mock_client_class.return_value = mock_client
    
    # Create provider with max_retries=1
    provider = AnthropicProvider({
        **SAMPLE_CONFIG,
        "max_retries": 1,  # Only 1 retry for this test
        "retry_delay": 0.1  # Shorter delay for testing
    })
    
    prepared_prompt = json.dumps({
        "prompt": "Test prompt",
        "messages": [{"role": "user", "content": "Test prompt"}],
        "system": "Test system"
    })
    
    # Verify the call raises TransientError with the expected message
    with pytest.raises(TransientError, match="Request failed after 2 attempts"):
        await provider.call(prepared_prompt)
    
    # Should have made 2 attempts (initial + 1 retry)
    assert mock_client.request.await_count == 2
    
    # Should have slept once (for the retry)
    assert mock_sleep.await_count == 1


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_anthropic_provider_invalid_response(mock_client_class):
    """Test that the provider handles invalid API responses."""
    from src.providers.implementations.anthropic import AnthropicProvider
    from src.providers.interface import PermanentError
    
    # Create a mock client that returns an invalid response
    mock_client = AsyncMock()
    
    # Create a mock response that simulates an error from the API
    mock_invalid_response = MagicMock()
    mock_invalid_response.status_code = 400  # Bad Request
    mock_invalid_response.json.return_value = {
        "error": {
            "type": "invalid_request_error",
            "message": "Invalid request: missing required field 'messages'"
        }
    }
    
    # Configure the client to return the invalid response
    mock_client.request = AsyncMock(return_value=mock_invalid_response)
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    
    # Configure the client class to return our mock client
    mock_client_class.return_value = mock_client
    
    # Create provider
    provider = AnthropicProvider(SAMPLE_CONFIG)
    
    prepared_prompt = json.dumps({
        "prompt": "Test prompt",
        "messages": [{"role": "user", "content": "Test prompt"}],
        "system": "Test system"
    })
    
    # Verify the call raises PermanentError with the error message from the API
    with pytest.raises(PermanentError, match="Invalid request: missing required field 'messages'"):
        await provider.call(prepared_prompt)
    
    # Should have made exactly 1 attempt (no retries for invalid responses)
    assert mock_client.request.await_count == 1


def test_anthropic_provider_serialization():
    """Test that the provider can be serialized and deserialized."""
    from src.providers.implementations.anthropic import AnthropicProvider
    
    # Create a provider with some configuration
    provider = AnthropicProvider(SAMPLE_CONFIG)
    
    # Serialize to dict
    provider_dict = provider.to_dict()
    
    # Verify all config values are included
    for key, value in SAMPLE_CONFIG.items():
        assert provider_dict[key] == value
    
    # Create a new provider from the dict
    new_provider = AnthropicProvider.from_dict(provider_dict)
    
    # Verify the new provider has the same attributes
    assert new_provider.api_key == provider.api_key
    assert new_provider.model == provider.model
    assert new_provider.max_tokens == provider.max_tokens
    assert new_provider.temperature == provider.temperature
    assert new_provider.top_p == provider.top_p
    assert new_provider.top_k == provider.top_k
    assert new_provider.stop_sequences == provider.stop_sequences
    assert new_provider.timeout == provider.timeout
    assert new_provider.max_retries == provider.max_retries
