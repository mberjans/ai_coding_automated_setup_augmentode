"""
Failing edge-case tests for configuration loader (TICKET-002.02).

Covers:
- unknown provider fields are rejected
- negative attempts invalid
- missing API key env raises friendly error
"""

import os
import tempfile
import pytest


def test_unknown_provider_fields_rejected():
    from src.config.loader import load_config
    from src.config.models import ConfigValidationError

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(
            """
providers:
  anthropic:
    api_key_env: "ANTHROPIC_API_KEY"
    extra_field_not_allowed: true
"""
        )
        path = f.name

    try:
        with pytest.raises(ConfigValidationError):
            load_config(path)
    finally:
        os.unlink(path)


def test_negative_attempts_invalid():
    from src.config.loader import load_config
    from src.config.models import ConfigValidationError

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(
            """
generation:
  attempts: -1
"""
        )
        path = f.name

    try:
        with pytest.raises(ConfigValidationError):
            load_config(path)
    finally:
        os.unlink(path)


def test_missing_api_key_env_raises_friendly_error():
    from src.config.loader import load_config
    from src.config.models import ConfigValidationError

    if "MISSING_ENV_FOR_TEST" in os.environ:
        del os.environ["MISSING_ENV_FOR_TEST"]

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(
            """
providers:
  anthropic:
    api_key_env: "MISSING_ENV_FOR_TEST"
"""
        )
        path = f.name

    try:
        with pytest.raises(ConfigValidationError):
            load_config(path)
    finally:
        os.unlink(path)
