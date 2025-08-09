"""Tests for evaluation weight configuration loading and defaults.

Covers:
- Default equality of weights when no config is provided.
- Reading explicit weights from a YAML config file via load_config().
"""
import os
import tempfile

import pytest

from src.config.loader import load_config


def write_temp_yaml(content: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception:
        os.unlink(path)
        raise
    return path


def test_default_weights_are_equal():
    """When no config is provided, both weights default to 0.5 and are equal."""
    cfg = load_config(None)
    assert cfg.evaluation.weights.task_relevance == 0.5
    assert cfg.evaluation.weights.documentation_relevance == 0.5
    assert cfg.evaluation.weights.task_relevance == cfg.evaluation.weights.documentation_relevance


def test_read_weights_from_config_file():
    """Weights should be read from YAML config and override defaults."""
    yaml_text = (
        "evaluation:\n"
        "  weights:\n"
        "    task_relevance: 0.7\n"
        "    documentation_relevance: 0.3\n"
    )
    path = write_temp_yaml(yaml_text)
    try:
        cfg = load_config(path)
        assert cfg.evaluation.weights.task_relevance == 0.7
        assert cfg.evaluation.weights.documentation_relevance == 0.3
    finally:
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass


def test_missing_config_file_uses_defaults():
    """Missing path gracefully falls back to defaults with equal weights."""
    cfg = load_config("/nonexistent/path/to/config.yaml")
    assert cfg.evaluation.weights.task_relevance == 0.5
    assert cfg.evaluation.weights.documentation_relevance == 0.5
    assert cfg.evaluation.weights.task_relevance == cfg.evaluation.weights.documentation_relevance
