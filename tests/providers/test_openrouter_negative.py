"""Additional negative tests for OpenRouter provider adapter."""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from src.providers.implementations.openrouter import OpenRouterProvider
from src.providers.interface import AuthError


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_openrouter_invalid_api_key_401(mock_client_class):
    """Test that 401 errors are properly handled as AuthError."""
    config = {
        "api_key": "test-key",
        "model": "test-model"
    }
    
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mock_response.json.return_value = {"error": {"message": "Invalid API key"}}
    
    # Configure mock client
    mock_client = AsyncMock()
    mock_client.request = AsyncMock(return_value=mock_response)
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client_class.return_value = mock_client
    
    # Test call
    provider = OpenRouterProvider(config)
    
    # Prepare proper JSON prompt
    prepared_prompt = '{"messages": [{"role": "user", "content": "test"}]}'
    
    with pytest.raises(AuthError):
        await provider.call(prepared_prompt)


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_openrouter_forbidden_403(mock_client_class):
    """Test that 403 errors are properly handled as AuthError."""
    config = {
        "api_key": "test-key",
        "model": "test-model"
    }
    
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = "Forbidden"
    mock_response.json.return_value = {"error": {"message": "Forbidden"}}
    
    # Configure mock client
    mock_client = AsyncMock()
    mock_client.request = AsyncMock(return_value=mock_response)
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client_class.return_value = mock_client
    
    # Test call
    provider = OpenRouterProvider(config)
    
    # Prepare proper JSON prompt
    prepared_prompt = '{"messages": [{"role": "user", "content": "test"}]}'
    
    with pytest.raises(AuthError):
        await provider.call(prepared_prompt)
