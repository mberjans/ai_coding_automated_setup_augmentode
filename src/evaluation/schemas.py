"""Functional helpers for evaluation.json schema and validation.

Avoids OOP; exposes simple functions to build and validate evaluation entries.
"""
from typing import Any, Dict


def build_evaluation_entry(task_score: float,
                           task_rationale: str,
                           doc_score: float,
                           doc_rationale: str,
                           weight_task: float,
                           weight_doc: float) -> Dict[str, Any]:
    """Build a normalized evaluation entry with combined score.

    All scores and weights must be within [0.0, 1.0]. Weights are not required to
    sum to 1.0 but the combined score uses them directly as linear weights.
    """
    _validate_float_0_1(task_score, "task_relevance.score")
    _validate_float_0_1(doc_score, "documentation_relevance.score")
    _validate_float_0_1(weight_task, "weights.task_relevance")
    _validate_float_0_1(weight_doc, "weights.documentation_relevance")
    _validate_non_empty_string(task_rationale, "task_relevance.rationale")
    _validate_non_empty_string(doc_rationale, "documentation_relevance.rationale")

    combined = (task_score * weight_task) + (doc_score * weight_doc)
    if combined < 0.0:
        combined = 0.0
    if combined > 1.0:
        combined = 1.0

    return {
        "task_relevance": {
            "score": float(task_score),
            "rationale": str(task_rationale),
        },
        "documentation_relevance": {
            "score": float(doc_score),
            "rationale": str(doc_rationale),
        },
        "weights": {
            "task_relevance": float(weight_task),
            "documentation_relevance": float(weight_doc),
        },
        "combined_score": float(combined),
    }


def validate_evaluation(data: Dict[str, Any]) -> None:
    """Validate an evaluation dictionary in-place.

    Raises ValueError on validation failures.
    """
    if not isinstance(data, dict):
        raise ValueError("evaluation must be a dict")

    if "task_relevance" not in data or not isinstance(data["task_relevance"], dict):
        raise ValueError("missing or invalid task_relevance")
    if "documentation_relevance" not in data or not isinstance(data["documentation_relevance"], dict):
        raise ValueError("missing or invalid documentation_relevance")
    if "weights" not in data or not isinstance(data["weights"], dict):
        raise ValueError("missing or invalid weights")

    _validate_float_0_1(_get_in(data, ["task_relevance", "score"]), "task_relevance.score")
    _validate_non_empty_string(_get_in(data, ["task_relevance", "rationale"]), "task_relevance.rationale")

    _validate_float_0_1(_get_in(data, ["documentation_relevance", "score"]), "documentation_relevance.score")
    _validate_non_empty_string(_get_in(data, ["documentation_relevance", "rationale"]), "documentation_relevance.rationale")

    _validate_float_0_1(_get_in(data, ["weights", "task_relevance"]), "weights.task_relevance")
    _validate_float_0_1(_get_in(data, ["weights", "documentation_relevance"]), "weights.documentation_relevance")

    # combined_score optional but if present validate range
    if "combined_score" in data:
        _validate_float_0_1(data["combined_score"], "combined_score")


def _validate_float_0_1(value: Any, name: str) -> None:
    if not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number between 0.0 and 1.0")
    f = float(value)
    if f < 0.0 or f > 1.0:
        raise ValueError(f"{name} must be within [0.0, 1.0]")


def _validate_non_empty_string(value: Any, name: str) -> None:
    if not isinstance(value, str) or len(value.strip()) == 0:
        raise ValueError(f"{name} must be a non-empty string")


def _get_in(obj: Dict[str, Any], path: list) -> Any:
    """Explicit path traversal without regex or comprehensions."""
    current = obj
    idx = 0
    while idx < len(path):
        key = path[idx]
        if not isinstance(current, dict) or key not in current:
            raise ValueError(f"missing required field: {'/'.join(str(p) for p in path)}")
        current = current[key]
        idx = idx + 1
    return current
