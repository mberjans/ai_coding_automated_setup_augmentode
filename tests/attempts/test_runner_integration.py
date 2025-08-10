import os
import tempfile
import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from typing import Dict, Any, Type

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


def test_run_attempt_with_provider():
    """Test running an attempt with a mock provider."""
    # Import inside test to ensure we get the latest version
    from src.attempts import runner
    from src.attempts.manifest import get_attempt_manifest
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup test data
        config = {
            "provider": "test_provider",
            "model": "test_model",
            "developer_name": "test_developer"
        }
        
        # Create a mock provider instance
        mock_provider = Mock()
        mock_provider.prepare_prompt.return_value = "formatted_prompt"
        mock_provider.call.return_value = {
            "content": "test response",
            "usage": {"total_tokens": 100}
        }
        
        # Create a mock provider class that returns our mock instance
        class MockProviderClass:
            def __init__(self, config):
                self.config = config
                self.mock = mock_provider
                
            def prepare_prompt(self, *args, **kwargs):
                return self.mock.prepare_prompt(*args, **kwargs)
                
            def call(self, *args, **kwargs):
                return self.mock.call(*args, **kwargs)
        
        # Mock the provider registry
        with patch('src.providers.registry._REGISTRY', {"test_provider": MockProviderClass}):
            # Run the attempt
            attempt_dir = runner.run_attempt(
                base_dir=temp_dir,
                config=config,
                prompt_bundle={
                    "plan": "test plan prompt",
                    "tickets": "test tickets prompt",
                    "checklist": "test checklist prompt"
                },
                processed_docs=[],
                provider_name="test_provider"
            )
        
        # Verify attempt directory structure
        assert os.path.isdir(attempt_dir)
        assert os.path.isfile(os.path.join(attempt_dir, "attempt_manifest.json"))
        assert os.path.isdir(os.path.join(attempt_dir, "outputs"))
        
        # Verify manifest content
        manifest_path = os.path.join(attempt_dir, "attempt_manifest.json")
        manifest_data = get_attempt_manifest(manifest_path)
        
        assert manifest_data["status"] == "completed"
        assert manifest_data["parameters"]["provider"] == "test_provider"
        assert manifest_data["parameters"]["model"] == "test_model"
        assert "metrics" in manifest_data
        assert "total_tokens" in manifest_data["metrics"]
        
        # Verify provider was called correctly
        mock_provider.prepare_prompt.assert_called_once()
        mock_provider.call.assert_called_once_with("formatted_prompt")


def test_run_attempt_error_handling():
    """Test error handling during attempt execution."""
    from src.attempts import runner
    from src.attempts.manifest import get_attempt_manifest
    from src.providers.interface import ProviderError
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup test data with invalid provider
        config = {
            "provider": "invalid_provider",
            "model": "test_model",
            "developer_name": "test_developer"
        }
        
        # Mock the provider registry to raise an exception
        with patch('src.providers.registry._REGISTRY', {}):
            # Run the attempt - should raise an exception
            with pytest.raises(ProviderError, match="Unknown provider"):
                runner.run_attempt(
                    base_dir=temp_dir,
                    config=config,
                    prompt_bundle={"plan": "test"},
                    processed_docs=[],
                    provider_name="invalid_provider"
                )
        
        # Verify the attempt directory was created but marked as failed
        attempt_dir = os.path.join(temp_dir, "invalid_provider_test_developer_test_model_attempt_1")
        assert os.path.isdir(attempt_dir)
        
        # Check that manifest exists and has failed status
        manifest_path = os.path.join(attempt_dir, "attempt_manifest.json")
        assert os.path.isfile(manifest_path)
        
        manifest_data = get_attempt_manifest(manifest_path)
        assert manifest_data["status"] == "failed"
        assert "error" in manifest_data


def test_get_next_attempt_number():
    """Test getting the next attempt number for a provider."""
    runner = __import__("src.attempts.runner", fromlist=["_get_next_attempt_number"])
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test attempt directories
        os.makedirs(os.path.join(temp_dir, "test_provider_test_dev_test_model_attempt_1"))
        os.makedirs(os.path.join(temp_dir, "test_provider_test_dev_test_model_attempt_3"))
        
        # Test getting next attempt number
        next_num = runner._get_next_attempt_number(
            base_dir=temp_dir,
            provider_name="test_provider",
            developer_name="test_dev",
            model_name="test_model"
        )
        
        # Should be 4 (existing: 1,3 -> next: 4)
        assert next_num == 4
        
        # Test with no existing attempts
        next_num = runner._get_next_attempt_number(
            base_dir=temp_dir,
            provider_name="other_provider",
            developer_name="test_dev",
            model_name="test_model"
        )
        assert next_num == 1


def test_run_attempt_provider_error_records_manifest_and_bubbles():
    """If provider.call raises ProviderError, runner should write failed manifest and raise."""
    from src.attempts import runner
    from src.attempts.manifest import get_attempt_manifest
    from src.providers.interface import ProviderError
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config = {
            "provider": "error_provider",
            "model": "test_model",
            "developer_name": "test_developer"
        }
        
        class ErrorProviderClass:
            def __init__(self, cfg):
                self.cfg = cfg
            def prepare_prompt(self, *args, **kwargs):
                return "formatted_prompt"
            def call(self, *args, **kwargs):
                raise ProviderError("simulated provider failure")
        
        with patch('src.providers.registry._REGISTRY', {"error_provider": ErrorProviderClass}):
            with pytest.raises(ProviderError, match="simulated provider failure"):
                runner.run_attempt(
                    base_dir=temp_dir,
                    config=config,
                    prompt_bundle={"plan": "p"},
                    processed_docs=[],
                    provider_name="error_provider"
                )
        
        attempt_dir = os.path.join(temp_dir, "error_provider_test_developer_test_model_attempt_1")
        assert os.path.isdir(attempt_dir)
        manifest_path = os.path.join(attempt_dir, "attempt_manifest.json")
        assert os.path.isfile(manifest_path)
        manifest_data = get_attempt_manifest(manifest_path)
        assert manifest_data["status"] == "failed"
        assert "error" in manifest_data
