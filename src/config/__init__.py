"""Configuration package for loading and validating app configuration.

Exports:
- load_config: main entry to load configuration from path or defaults
- ConfigValidationError: raised when configuration is invalid
- AppConfig and related Pydantic models
"""

from .models import (
    AppConfig,
    ProviderConfig,
    GenerationConfig,
    EvaluationConfig,
    RateLimits,
    LoggingConfig,
    ConfigValidationError,
)
from .loader import load_config
