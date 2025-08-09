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
