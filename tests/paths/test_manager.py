"""
Failing tests for Path/Directory Manager (TICKET-004.01).

Ensures required directories are created if missing and creation is idempotent.
"""
from pathlib import Path
import tempfile


def test_required_directories_created_and_idempotent():
    from src.paths.manager import ensure_required_dirs

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)

        # Ensure required dirs are created
        result = ensure_required_dirs(str(base))
        assert (base / "processed_documents" / "text").exists()
        assert (base / "COMBINED_RESULTS").exists()
        assert (base / "logs").exists()

        # Return value should include created paths
        assert "processed_text" in result
        assert "combined_results" in result
        assert "logs" in result

        # Idempotent call should not fail and paths should remain
        result2 = ensure_required_dirs(str(base))
        assert (base / "processed_documents" / "text").exists()
        assert (base / "COMBINED_RESULTS").exists()
        assert (base / "logs").exists()

        # Returned paths match
        assert result["processed_text"] == result2["processed_text"]
        assert result["combined_results"] == result2["combined_results"]
        assert result["logs"] == result2["logs"]
