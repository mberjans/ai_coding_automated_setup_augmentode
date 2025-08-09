"""Tests for judge scoring (TICKET-018.01)."""
import pytest
from src.evaluation.judge import score_task_relevance, score_documentation_relevance


def test_score_task_relevance_returns_float_between_0_and_1():
    """Test that task_relevance scoring returns a float in [0.0, 1.0]."""
    result = score_task_relevance("test prompt", "test response")
    assert isinstance(result, dict)
    assert "score" in result
    assert isinstance(result["score"], float)
    assert 0.0 <= result["score"] <= 1.0


def test_score_task_relevance_includes_rationale():
    """Test that task_relevance scoring includes a rationale."""
    result = score_task_relevance("test prompt", "test response")
    assert "rationale" in result
    assert isinstance(result["rationale"], str)


def test_score_documentation_relevance_returns_float_between_0_and_1():
    """Test that documentation_relevance scoring returns a float in [0.0, 1.0]."""
    result = score_documentation_relevance("test prompt", "test response")
    assert isinstance(result, dict)
    assert "score" in result
    assert isinstance(result["score"], float)
    assert 0.0 <= result["score"] <= 1.0


def test_score_documentation_relevance_includes_rationale():
    """Test that documentation_relevance scoring includes a rationale."""
    result = score_documentation_relevance("test prompt", "test response")
    assert "rationale" in result
    assert isinstance(result["rationale"], str)


def test_score_task_relevance_with_empty_response():
    """Test task_relevance scoring with empty response."""
    result = score_task_relevance("test prompt", "")
    assert isinstance(result, dict)
    assert result["score"] == 0.0


def test_score_documentation_relevance_with_empty_response():
    """Test documentation_relevance scoring with empty response."""
    result = score_documentation_relevance("test prompt", "")
    assert isinstance(result, dict)
    assert result["score"] == 0.0
