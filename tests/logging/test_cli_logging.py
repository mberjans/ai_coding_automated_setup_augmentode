"""
Failing tests for CLI logging wiring (TICKET-003.05).

Checks that:
- CLI emits JSON logs to console.
- --verbose enables DEBUG-level output; default hides DEBUG.
"""
import sys
import subprocess
import json


def _run_cli(args):
    cmd = [sys.executable, "-m", "src.cli"]
    for a in args:
        cmd.append(a)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def _collect_json_lines(text):
    lines = []
    for part in text.splitlines():
        if part.strip():
            lines.append(part)
    records = []
    for line in lines:
        try:
            records.append(json.loads(line))
        except Exception:
            # ignore non-JSON output lines
            pass
    return records


def test_cli_default_hides_debug():
    code, out, err = _run_cli(["run"])  # default, no --verbose
    assert code == 0
    # logs may go to stdout; combine
    text = out
    if err:
        text = text + err
    records = _collect_json_lines(text)
    saw_info = False
    saw_debug = False
    for r in records:
        if r.get("level") == "INFO" and r.get("message") == "cli initialized":
            saw_info = True
        if r.get("level") == "DEBUG" and r.get("message") == "cli initialized debug":
            saw_debug = True
    assert saw_info
    assert not saw_debug


def test_cli_verbose_shows_debug():
    code, out, err = _run_cli(["--verbose", "run"])  # with --verbose
    assert code == 0
    text = out
    if err:
        text = text + err
    records = _collect_json_lines(text)
    saw_info = False
    saw_debug = False
    for r in records:
        if r.get("level") == "INFO" and r.get("message") == "cli initialized":
            saw_info = True
        if r.get("level") == "DEBUG" and r.get("message") == "cli initialized debug":
            saw_debug = True
    assert saw_info
    assert saw_debug
