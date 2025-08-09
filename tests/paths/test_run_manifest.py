"""
Failing tests for run_manifest.json save/load with atomic writes (TICKET-004.05).
"""
from pathlib import Path
import tempfile
import time


def test_run_manifest_roundtrip_and_atomic():
    from src.paths.manifests import save_run_manifest, load_run_manifest

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        run_manifest = base / "run_manifest.json"

        data = {
            "run_id": "abc123",
            "started_at": str(int(time.time())),
            "providers": [
                {"provider": "Anthropic", "developer": "Anthropic", "model": "claude-3-sonnet"},
                {"provider": "OpenRouter", "developer": "OpenAI", "model": "gpt-4o"},
            ],
            "weights": {"task_relevance": 1.0, "documentation_relevance": 1.0},
        }

        save_run_manifest(str(run_manifest), data)
        assert run_manifest.exists()
        size1 = run_manifest.stat().st_size

        loaded = load_run_manifest(str(run_manifest))
        assert loaded == data

        # Overwrite again; size remains deterministic due to sorted keys
        save_run_manifest(str(run_manifest), data)
        size2 = run_manifest.stat().st_size
        assert size1 == size2
