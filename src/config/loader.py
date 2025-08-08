"""Configuration loader for the application (TICKET-002).

- Loads YAML from a provided path or uses defaults when missing.
- Validates key fields with explicit checks (no regex).
- For provider api_key_env, verifies that the environment variable exists,
  but never logs secrets or env var names.
"""
from __future__ import annotations

import os
import logging
from typing import Any, Dict, Optional

import yaml
from pydantic import ValidationError

from .models import AppConfig, ConfigValidationError, ProviderConfig
from .validation import (
    validate_temperature,
    validate_max_tokens,
    validate_attempts,
    validate_weight,
    validate_logging_level,
    validate_api_key_env,
)


_LOG = logging.getLogger("src.config")


def _load_yaml_file(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigValidationError("config file must contain a mapping at top-level")
    return data


def _dict_get(d: Dict[str, Any], key: str, default: Any) -> Any:
    if key in d:
        return d[key]
    return default


def _build_config_from_dict(data: Dict[str, Any]) -> AppConfig:
    try:
        cfg = AppConfig(**data)
    except ValidationError as e:
        # Convert pydantic validation errors into our specific error type
        raise ConfigValidationError(str(e))
    return cfg


def _validate_config(cfg: AppConfig) -> None:
    # generation
    validate_temperature(cfg.generation.temperature)
    validate_max_tokens(cfg.generation.max_tokens)
    validate_attempts(cfg.generation.attempts)

    # evaluation weights
    validate_weight(cfg.evaluation.weights.task_relevance, "task_relevance")
    validate_weight(
        cfg.evaluation.weights.documentation_relevance,
        "documentation_relevance",
    )

    # logging
    validate_logging_level(cfg.logging.level)

    # provider env var checks (only for known providers we model explicitly)
    if cfg.providers.anthropic is not None:
        _validate_provider_env(cfg.providers.anthropic)


def _validate_provider_env(provider: ProviderConfig) -> None:
    validate_api_key_env(provider.api_key_env)
    if provider.api_key_env is None:
        return
    env_name = provider.api_key_env
    # Do not log the env var name or value here to avoid leaking info
    if env_name not in os.environ:
        raise ConfigValidationError(
            "Missing required provider API key environment variable"
        )


def load_config(path: Optional[str] = None) -> AppConfig:
    """Load configuration from YAML file or defaults.

    Behavior:
    - If path is None, return default AppConfig() (no disk access).
    - If path is provided and file exists, load and validate it.
    - If path is provided but missing, return default AppConfig().
    - No secrets or env var names are logged.
    """
    if path is None:
        cfg = AppConfig()
        _validate_config(cfg)
        return cfg

    if not os.path.exists(path):
        # graceful fallback to defaults
        cfg = AppConfig()
        _validate_config(cfg)
        return cfg

    data = _load_yaml_file(path)
    cfg = _build_config_from_dict(data)
    _validate_config(cfg)

    # Avoid logging secrets or env var names entirely
    try:
        _LOG.debug("configuration loaded [REDACTED]")
    except Exception:
        # Even logging failures should not break config loading
        pass

    return cfg
