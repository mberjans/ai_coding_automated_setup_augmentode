"""
Path/Directory Manager (TICKET-004.01)

Provides utilities to ensure required directories exist.
Functional style, no regex, no list comprehensions.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict


def _ensure_dir(path: Path) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def _join(a: Path, b: str) -> Path:
    # Explicit join helper
    return a / b


def ensure_required_dirs(base_dir: str) -> Dict[str, str]:
    """Ensure required directories exist under base_dir.

    Creates (if missing):
    - processed_documents/text/
    - COMBINED_RESULTS/
    - logs/

    Returns a mapping with absolute string paths for convenience.
    """
    base = Path(base_dir).resolve()

    processed_root = _join(base, "processed_documents")
    processed_text = _join(processed_root, "text")
    combined_results = _join(base, "COMBINED_RESULTS")
    logs_dir = _join(base, "logs")

    _ensure_dir(processed_text)
    _ensure_dir(combined_results)
    _ensure_dir(logs_dir)

    result: Dict[str, str] = {}
    result["processed_text"] = str(processed_text)
    result["combined_results"] = str(combined_results)
    result["logs"] = str(logs_dir)
    return result


def _sanitize_segment(seg: str) -> str:
    # Replace any unsafe characters with underscore without regex
    if seg is None:
        return ""
    safe = []
    for ch in seg:
        # Allow alphanumerics, dash, underscore, dot
        ok = False
        if "0" <= ch <= "9":
            ok = True
        if "a" <= ch <= "z":
            ok = True
        if "A" <= ch <= "Z":
            ok = True
        if ch == "-" or ch == "_" or ch == ".":
            ok = True
        if ok:
            safe.append(ch)
        else:
            safe.append("_")
    # Join without list comprehension
    out = ""
    for c in safe:
        out = out + c
    return out


def _combine_provider_developer_model(provider: str, developer: str, model: str) -> str:
    # Create {Provider}_{Developer}_{Model} with sanitization
    p = _sanitize_segment(provider)
    d = _sanitize_segment(developer)
    m = _sanitize_segment(model)
    return p + "_" + d + "_" + m


def build_attempt_dir(base_dir: str, provider: str, developer: str, model: str, attempt_num: int) -> str:
    """Create and return absolute path to attempt directory.

    Format: {Provider}_{Developer}_{Model}/attempt_N
    """
    base = Path(base_dir).resolve()
    parent = _combine_provider_developer_model(provider, developer, model)
    parent_path = _join(base, parent)
    attempt_name = "attempt_" + str(int(attempt_num))
    attempt_path = _join(parent_path, attempt_name)
    _ensure_dir(attempt_path)
    return str(attempt_path)
