"""Pydantic models for application configuration (TICKET-002).

Note: We use Pydantic models as requested by the ticket. Additional explicit
validation (no regex) is applied in validation.py and the loader.
"""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class ConfigValidationError(Exception):
    """Raised when configuration is invalid or incomplete."""


class RateLimits(BaseModel):
    # Placeholder for future tests/tickets; keeping simple defaults.
    requests_per_minute: Optional[int] = Field(default=None)
    burst: Optional[int] = Field(default=None)


class Weights(BaseModel):
    task_relevance: float = Field(default=0.5)
    documentation_relevance: float = Field(default=0.5)


class EvaluationConfig(BaseModel):
    weights: Weights = Field(default_factory=Weights)


class GenerationConfig(BaseModel):
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=1024)
    attempts: int = Field(default=1)


class LoggingConfig(BaseModel):
    level: str = Field(default="INFO")
    file_path: Optional[str] = Field(default="logs/app.log")


class ProviderConfig(BaseModel):
    # env var name holding the API key
    api_key_env: Optional[str] = Field(default=None)
    # optional list of models supported/desired
    models: Optional[list[str]] = Field(default=None)

    model_config = {
        "extra": "forbid",  # reject unknown fields inside provider config
    }


class Providers(BaseModel):
    # We model explicit providers we know about to support attribute access
    # like config.providers.anthropic in tests. Others can be added later.
    anthropic: Optional[ProviderConfig] = Field(default=None)


class AppConfig(BaseModel):
    providers: Providers = Field(default_factory=Providers)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    rate_limits: Optional[RateLimits] = Field(default=None)

    model_config = {
        "extra": "ignore",  # ignore unknown top-level keys for forward-compat
    }
