"""
Failing tests for attempt path formatting (TICKET-004.02).

Format: {Provider}_{Developer}_{Model}/attempt_N/
"""
from pathlib import Path
import tempfile


def test_attempt_path_format_and_creation():
    from src.paths.manager import build_attempt_dir

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)

        p = build_attempt_dir(str(base), "Anthropic", "Mark", "claude-3-sonnet", 2)
        # Must exist and end with expected pattern
        assert Path(p).exists()
        expected_suffix = str(Path("Anthropic_Mark_claude-3-sonnet") / "attempt_2")
        assert str(p).endswith(expected_suffix)

        # Idempotent second call returns same path and still exists
        p2 = build_attempt_dir(str(base), "Anthropic", "Mark", "claude-3-sonnet", 2)
        assert p == p2
        assert Path(p2).exists()


essential_bad = ["OpenAI*", "Dev/Name", "gpt:4?mini"]


def test_sanitization_of_segments():
    from src.paths.manager import build_attempt_dir

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        p = build_attempt_dir(str(base), "OpenAI*", "Dev/Name", "gpt:4?mini", 1)
        # Ensure unsafe characters are replaced with '_'
        last = Path(p).parts[-2]  # {Provider}_{Developer}_{Model}
        # Validate absence of unsafe characters
        for ch in "*/:? ":
            assert ch not in last
        # Should contain underscores as replacements
        assert "_" in last
