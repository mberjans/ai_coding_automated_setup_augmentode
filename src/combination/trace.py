"""Trace utilities for combination engine: per-section citations and rationale.

Functional only; no OOP, no list comprehensions, no regex.
"""
import json
import os
from typing import Dict, List, Any


def _doc_names() -> List[str]:
    return ["plan.md", "tickets.md", "checklist.md"]


def build_trace_with_rationale(attempt_paths: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """Build a trace mapping each doc name to a list of {path, rationale}.

    Rationale is a simple string explaining inclusion origin.
    """
    trace: Dict[str, List[Dict[str, Any]]] = {}
    docs = _doc_names()
    di = 0
    while di < len(docs):
        name = docs[di]
        entries: List[Dict[str, Any]] = []
        i = 0
        while i < len(attempt_paths):
            p = attempt_paths[i]
            entries.append({
                "path": p,
                "rationale": "Included content from source attempt",
            })
            i = i + 1
        trace[name] = entries
        di = di + 1
    return trace


def write_trace(out_dir: str, trace: Dict[str, Any]) -> None:
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "trace.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2, ensure_ascii=False)
