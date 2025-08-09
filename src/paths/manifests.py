"""
Attempt manifest utilities (TICKET-004.03)
Functional style; no regex; no list comprehensions; error-safe writes.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict


def _write_atomic(target_path: Path, content: str) -> None:
    # Write to a temp file in same directory, then replace atomically
    directory = target_path.parent
    tmp_path = directory / (target_path.name + ".tmp")

    # Ensure parent exists
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)

    with tmp_path.open("w", encoding="utf-8") as f:
        f.write(content)

    # Replace existing file atomically when possible
    os.replace(str(tmp_path), str(target_path))



def save_attempt_manifest(manifest_path: str, data: Dict[str, Any]) -> None:
    path = Path(manifest_path)
    # Serialize with stable key order for deterministic size and roundtrip
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    _write_atomic(path, text)



def load_attempt_manifest(manifest_path: str) -> Dict[str, Any]:
    path = Path(manifest_path)
    with path.open("r", encoding="utf-8") as f:
        text = f.read()
    # Parse JSON to dict
    obj = json.loads(text)
    # Ensure types are mapping-like
    if not isinstance(obj, dict):
        raise ValueError("attempt_manifest must be a JSON object")
    return obj
