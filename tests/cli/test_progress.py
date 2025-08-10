import io
from time import sleep

from rich.console import Console

from src.cli_progress import display_progress


def test_progress_displays_stages_and_summary():
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=False, color_system=None, width=80, legacy_windows=False)
    stages = ["process-docs", "generate", "evaluate", "combine"]

    summary = display_progress(stages, console=console, step_delay=0.0)

    out = buf.getvalue()
    # Expect stage names to appear in the output
    for s in stages:
        assert s in out
    # Expect a final summary line
    assert "Completed pipeline" in out

    # Summary content
    assert isinstance(summary, dict)
    assert summary.get("total_stages") == len(stages)
    assert len(summary.get("durations", {})) == len(stages)
