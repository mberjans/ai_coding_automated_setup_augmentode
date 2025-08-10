"""Ranking and metadata helpers for evaluation results.

Functional style; no OOP, no list comprehensions, no regex.
"""
import json
import os
from typing import Any, Dict, List

from .schemas import validate_evaluation


def _get_weight(weights: Dict[str, Any], key: str, default: float) -> float:
    if not isinstance(weights, dict):
        return float(default)
    value = weights.get(key, default)
    try:
        f = float(value)
    except Exception:
        f = float(default)
    if f < 0.0:
        f = 0.0
    if f > 1.0:
        f = 1.0
    return f


essential_weight_keys = ("task_relevance", "documentation_relevance")


def _combined_from_evaluation(evaluation: Dict[str, Any], weights: Dict[str, Any]) -> float:
    # Validate expected structure
    validate_evaluation(evaluation)
    wt = _get_weight(weights, "task_relevance", 0.5)
    wd = _get_weight(weights, "documentation_relevance", 0.5)
    ts = float(evaluation["task_relevance"]["score"])  # already validated bounds
    ds = float(evaluation["documentation_relevance"]["score"])  # already validated bounds
    combined = (ts * wt) + (ds * wd)
    if combined < 0.0:
        combined = 0.0
    if combined > 1.0:
        combined = 1.0
    return combined


def _task_score_for_tiebreak(evaluation: Dict[str, Any]) -> float:
    try:
        return float(evaluation.get("task_relevance", {}).get("score", 0.0))
    except Exception:
        return 0.0


def _model_name(item: Dict[str, Any]) -> str:
    m = item.get("model", "")
    if not isinstance(m, str):
        return ""
    return m


def rank_attempts(attempts: List[Dict[str, Any]], weights: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return a new list of attempts sorted by combined_score desc, with tie-breakers.

    - combined_score: computed from evaluation if missing
    - tie-breakers: higher task_relevance.score, then model name ascending
    """
    # Copy input to avoid mutation
    ranked: List[Dict[str, Any]] = []
    idx = 0
    while idx < len(attempts):
        item = attempts[idx]
        # Shallow copy
        copy_item = {}
        for k in item:
            copy_item[k] = item[k]
        # Ensure combined_score present
        if "combined_score" not in copy_item:
            if "evaluation" in copy_item:
                try:
                    combined = _combined_from_evaluation(copy_item["evaluation"], weights)
                except Exception:
                    combined = 0.0
            else:
                combined = 0.0
            copy_item["combined_score"] = float(combined)
        ranked.append(copy_item)
        idx = idx + 1

    # Sort using tie-breakers. We cannot use list comprehensions; build a key tuple for each.
    def sort_key(d: Dict[str, Any]):
        # Negative for descending combined and task score, string normal for model asc
        combined = float(d.get("combined_score", 0.0))
        task_score = 0.0
        if isinstance(d.get("evaluation"), dict):
            task_score = _task_score_for_tiebreak(d["evaluation"])
        model = _model_name(d)
        return (-combined, -task_score, model)

    ranked.sort(key=sort_key)
    return ranked


def build_metadata(baseline_path: str, weights: Dict[str, Any], ranked: List[Dict[str, Any]]) -> Dict[str, Any]:
    meta_ranked: List[Dict[str, Any]] = []
    i = 0
    while i < len(ranked):
        r = ranked[i]
        entry = {
            "path": r.get("path"),
            "model": r.get("model"),
            "combined_score": float(r.get("combined_score", 0.0)),
        }
        meta_ranked.append(entry)
        i = i + 1

    return {
        "baseline_path": baseline_path,
        "weights": {
            "task_relevance": _get_weight(weights, "task_relevance", 0.5),
            "documentation_relevance": _get_weight(weights, "documentation_relevance", 0.5),
        },
        "ranked": meta_ranked,
    }


def write_metadata(out_dir: str, metadata: Dict[str, Any]) -> None:
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "metadata.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
