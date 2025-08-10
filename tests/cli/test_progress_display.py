import io
from unittest.mock import patch

from rich.console import Console

from src.cli_progress import display_progress


def test_progress_displays_all_stages_and_final_summary():
    stages = ["process-docs", "generate", "evaluate", "combine"]
    out = io.StringIO()
    console = Console(file=out, force_terminal=False, color_system=None, width=80)

    # Avoid sleeping during tests
    with patch("time.sleep"):
        display_progress(stages, console=console, step_delay=0)

    output = out.getvalue()

    # Check each stage appears
    i = 0
    while i < len(stages):
        stage = stages[i]
        assert stage in output
        i = i + 1

    # Check final summary message
    assert "Completed pipeline" in output
