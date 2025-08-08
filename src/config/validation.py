"""Explicit validation helpers for configuration values (no regex)."""
from __future__ import annotations

from typing import Optional

from .models import ConfigValidationError


def _is_number(value) -> bool:
    try:
        float(value)
        return True
    except Exception:
        return False


def validate_temperature(value: float) -> None:
    if not _is_number(value):
        raise ConfigValidationError("temperature must be a number")
    if value < 0.0:
        raise ConfigValidationError("temperature must be >= 0.0")
    if value > 2.0:
        raise ConfigValidationError("temperature must be <= 2.0")


def validate_max_tokens(value: int) -> None:
    if not isinstance(value, int):
        raise ConfigValidationError("max_tokens must be an integer")
    if value <= 0:
        raise ConfigValidationError("max_tokens must be positive")


def validate_attempts(value: int) -> None:
    if not isinstance(value, int):
        raise ConfigValidationError("attempts must be an integer")
    if value < 0:
        raise ConfigValidationError("attempts cannot be negative")


def validate_weight(value: float, name: str) -> None:
    if not _is_number(value):
        raise ConfigValidationError(f"{name} must be a number")
    if value < 0.0:
        raise ConfigValidationError(f"{name} must be >= 0.0")
    if value > 1.0:
        raise ConfigValidationError(f"{name} must be <= 1.0")


def validate_logging_level(level: str) -> None:
    # Accept common levels only
    allowed = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}
    if not isinstance(level, str):
        raise ConfigValidationError("logging.level must be a string")
    upper = level.upper()
    if upper not in allowed:
        raise ConfigValidationError("invalid logging level")


def validate_api_key_env(name: Optional[str]) -> None:
    if name is None:
        return
    if not isinstance(name, str):
        raise ConfigValidationError("api_key_env must be a string if provided")
    # Disallow empty or whitespace-only
    stripped = name.strip()
    if len(stripped) == 0:
        raise ConfigValidationError("api_key_env cannot be empty")
