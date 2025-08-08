import os
from pathlib import Path

import pytest

# TICKET-005.02: Failing tests for unknown/unsupported extensions → skipped with reason; ensure logs contain skip entry.

UNKNOWN_CASES = [
    "archive.zip",
    "movie.mp4",
    "audio.wav",
    "binary.bin",
    "noext",
]


@pytest.mark.parametrize("filename", UNKNOWN_CASES)
def test_unknown_extension_returns_none_and_logs_skip_from_str(caplog, filename):
    from src.processing import detection

    caplog.clear()
    caplog.set_level("INFO")

    path_str = os.path.join("/tmp", filename)
    result = detection.detect_handler(path_str)
    assert result is None

    # Ensure a skip entry is logged with a reason mentioning unsupported extension
    found = False
    for record in caplog.records:
        text = str(record.msg)
        if "skip" in text.lower() and "unsupported" in text.lower():
            found = True
            break
    assert found


@pytest.mark.parametrize("filename", UNKNOWN_CASES)
def test_unknown_extension_returns_none_and_logs_skip_from_path(caplog, filename):
    from src.processing import detection

    caplog.clear()
    caplog.set_level("INFO")

    path_obj = Path("/tmp") / filename
    result = detection.detect_handler(path_obj)
    assert result is None

    found = False
    for record in caplog.records:
        text = str(record.msg)
        if "skip" in text.lower() and "unsupported" in text.lower():
            found = True
            break
    assert found
