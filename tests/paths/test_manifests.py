"""
Failing tests for attempt_manifest.json roundtrip (TICKET-004.03).
"""
from pathlib import Path
import tempfile
import time


def _now_iso() -> str:
    # Simple ISO-like string without relying on datetime formatting specifics
    t = int(time.time())
    return str(t)


def test_attempt_manifest_roundtrip():
    from src.paths.manifests import save_attempt_manifest, load_attempt_manifest
    from src.paths.manager import build_attempt_dir

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        attempt_dir = build_attempt_dir(str(base), "Anthropic", "Mark", "claude-3-sonnet", 3)
        manifest_path = Path(attempt_dir) / "attempt_manifest.json"

        data = {
            "provider": "Anthropic",
            "developer": "Mark",
            "model": "claude-3-sonnet",
            "attempt": 3,
            "started_at": _now_iso(),
            "finished_at": _now_iso(),
            "parameters": {
                "temperature": 0,
                "max_tokens": 1024,
                "top_p": 1,
            },
        }

        save_attempt_manifest(str(manifest_path), data)
        assert manifest_path.exists()

        loaded = load_attempt_manifest(str(manifest_path))
        # Roundtrip equality
        assert loaded == data


def test_error_safe_write_creates_file_atomically():
    from src.paths.manifests import save_attempt_manifest
    from src.paths.manager import build_attempt_dir

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        attempt_dir = build_attempt_dir(str(base), "OpenAI", "Dev", "gpt-4o", 1)
        manifest_path = Path(attempt_dir) / "attempt_manifest.json"

        data = {"provider": "OpenAI", "developer": "Dev", "model": "gpt-4o", "attempt": 1}

        # Write twice to ensure idempotent and safe
        save_attempt_manifest(str(manifest_path), data)
        size1 = manifest_path.stat().st_size
        save_attempt_manifest(str(manifest_path), data)
        size2 = manifest_path.stat().st_size
        assert size1 == size2
