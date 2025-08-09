"""Tests for the OpenRouter provider adapter."""
import json
import os
from unittest.mock import MagicMock, patch, AsyncMock
import pytest
import httpx

# Enable asyncio mode for tests
pytestmark = pytest.mark.asyncio

from src.providers.interface import AuthError, RateLimitError, TransientError

# Sample configuration for tests
SAMPLE_CONFIG = {
    "api_key": "test-api-key",
    "model": "openai/gpt-4-turbo",
    "max_tokens": 1000,
    "temperature": 0.7,
    "headers": {
        "HTTP-Referer": "https://example.com"
    }
}

# Sample API response
SAMPLE_RESPONSE = {
    "choices": [{"message": {"content": "Test response"}}],
    "usage": {"total_tokens": 30}
}


def test_openrouter_provider_initialization():
    """Test that OpenRouterProvider initializes with valid config."""
    from src.providers.implementations.openrouter import OpenRouterProvider
    
    provider = OpenRouterProvider(SAMPLE_CONFIG)
    assert provider.model == "openai/gpt-4-turbo"
    assert provider.api_key == "test-api-key"
    assert provider.headers["HTTP-Referer"] == "https://example.com"


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_openrouter_provider_call_success(mock_client_class):
    """Test successful API call to OpenRouter."""
    from src.providers.implementations.openrouter import OpenRouterProvider
    
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = SAMPLE_RESPONSE
    
    # Configure mock client
    mock_client = AsyncMock()
    mock_client.request = AsyncMock(return_value=mock_response)
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client_class.return_value = mock_client
    
    # Test call
    provider = OpenRouterProvider(SAMPLE_CONFIG)
    prepared_prompt = json.dumps({
        "messages": [{"role": "user", "content": "Test"}],
        "system": "Test system"
    })
    
    result = await provider.call(prepared_prompt)
    assert result["content"] == "Test response"
    assert mock_client.request.await_count == 1
