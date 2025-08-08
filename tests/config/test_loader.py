"""
Failing tests for configuration loader functionality.

Tests for TICKET-002.01:
- default config load
- custom path load  
- validation errors
- env var secret mapping
"""

import os
import tempfile
import pytest
from pathlib import Path


def test_load_default_config():
    """Test loading default configuration file."""
    # This will fail until src/config/loader.py is implemented
    from src.config.loader import load_config
    
    config = load_config()
    
    # Should load from default location and have basic structure
    assert config is not None
    assert hasattr(config, 'providers')
    assert hasattr(config, 'generation')
    assert hasattr(config, 'evaluation')
    assert hasattr(config, 'logging')


def test_load_custom_path_config():
    """Test loading configuration from custom path."""
    from src.config.loader import load_config
    
    # Use fixture config file
    from pathlib import Path
    fixture_path = Path(__file__).parent.parent / "fixtures" / "configs" / "valid_config.yaml"
    
    try:
        # Provide the expected env var for the test
        os.environ["ANTHROPIC_API_KEY"] = "dummy-key"
        config = load_config(str(fixture_path))
        
        assert config is not None
        assert config.providers.anthropic.api_key_env == "ANTHROPIC_API_KEY"
        assert config.generation.temperature == 0.7
        assert config.evaluation.weights.task_relevance == 0.6
        assert config.logging.level == "INFO"
    finally:
        if "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]


def test_validation_errors_on_invalid_config():
    """Test that validation errors are raised for invalid configuration."""
    from src.config.loader import load_config
    from src.config.models import ConfigValidationError
    
    # Create invalid config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
providers:
  anthropic:
    api_key_env: ""  # Empty API key env should be invalid
generation:
  temperature: 2.5  # Invalid temperature > 2.0
  max_tokens: -100  # Negative tokens invalid
evaluation:
  weights:
    task_relevance: 1.5  # Invalid weight > 1.0
logging:
  level: "INVALID_LEVEL"  # Invalid log level
""")
        temp_path = f.name
    
    try:
        with pytest.raises(ConfigValidationError):
            load_config(temp_path)
    finally:
        os.unlink(temp_path)


def test_env_var_secret_mapping():
    """Test that API keys are properly mapped from environment variables."""
    from src.config.loader import load_config
    
    # Set test environment variable
    test_api_key = "test-api-key-12345"
    os.environ["TEST_ANTHROPIC_KEY"] = test_api_key
    
    # Create config that references the env var
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
providers:
  anthropic:
    api_key_env: "TEST_ANTHROPIC_KEY"
    models:
      - "claude-3-sonnet-20240229"
generation:
  temperature: 0.7
evaluation:
  weights:
    task_relevance: 0.6
    documentation_relevance: 0.4
logging:
  level: "INFO"
""")
        temp_path = f.name
    
    try:
        config = load_config(temp_path)
        
        # Should resolve the API key from environment
        assert config.providers.anthropic.api_key_env == "TEST_ANTHROPIC_KEY"
        # The actual API key should be accessible but not stored in config
        assert os.getenv("TEST_ANTHROPIC_KEY") == test_api_key
    finally:
        os.unlink(temp_path)
        if "TEST_ANTHROPIC_KEY" in os.environ:
            del os.environ["TEST_ANTHROPIC_KEY"]


def test_missing_config_file_uses_defaults():
    """Test that missing config file falls back to sensible defaults."""
    from src.config.loader import load_config
    
    # Try to load non-existent file
    config = load_config("/path/that/does/not/exist.yaml")
    
    # Should return default configuration
    assert config is not None
    assert hasattr(config, 'providers')
    assert hasattr(config, 'generation')
    assert hasattr(config, 'evaluation')
    assert hasattr(config, 'logging')


def test_config_secrets_not_logged():
    """Test that API keys and secrets are not included in logs."""
    from src.config.loader import load_config
    import logging
    from io import StringIO
    
    # Set up string capture for logs
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    logger = logging.getLogger('src.config')
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    # Set environment variable with secret
    os.environ["SECRET_API_KEY"] = "super-secret-key-12345"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
providers:
  anthropic:
    api_key_env: "SECRET_API_KEY"
generation:
  temperature: 0.7
""")
        temp_path = f.name
    
    try:
        load_config(temp_path)
        
        # Check that secret is not in logs
        log_output = log_capture.getvalue()
        assert "super-secret-key-12345" not in log_output
        assert "SECRET_API_KEY" not in log_output or "[REDACTED]" in log_output
    finally:
        os.unlink(temp_path)
        if "SECRET_API_KEY" in os.environ:
            del os.environ["SECRET_API_KEY"]
        logger.removeHandler(handler)
