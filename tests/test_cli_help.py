import sys
import subprocess


def test_cli_help_exits_zero_and_lists_commands():
    cmd = [sys.executable, "-m", "src.cli", "--help"]
    proc = subprocess.run(cmd, capture_output=True, text=True)

    output = proc.stdout
    if proc.stderr:
        output = output + proc.stderr

    assert proc.returncode == 0

    lower = output.lower()
    assert "usage" in lower
    assert "run" in lower
    assert "process-docs" in lower
    assert "generate" in lower
    assert "evaluate" in lower
    assert "combine" in lower
