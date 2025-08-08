"""
Failing tests for logging handlers (TICKET-003.02).

Asserts:
- Rotating file handler writes JSON lines to provided file path.
- Console handler level respects provided level (e.g., WARNING ignores INFO).
"""

import json
import logging
import os
from io import StringIO
from pathlib import Path
import tempfile

from src.logging.json_logger import get_logger


def test_rotating_file_handler_writes_to_file():
    from src.logging.handlers import get_file_handler

    with tempfile.TemporaryDirectory() as tmp:
        log_dir = Path(tmp) / "logs"
        file_path = log_dir / "app.log"

        logger = get_logger("test.handlers.file", level="INFO")
        fh = get_file_handler(str(file_path))

        logger.handlers = []
        logger.addHandler(fh)
        logger.setLevel(logging.INFO)

        logger.info("file handler write test")

        assert file_path.exists(), "log file not created"
        content = file_path.read_text().strip()
        assert content, "log file empty"

        # last line must be valid JSON
        last_line = content.splitlines()[-1]
        record = json.loads(last_line)
        assert record["message"] == "file handler write test"
        assert record["level"] == "INFO"
        assert record["name"] == "test.handlers.file"


def test_console_level_respects_config():
    from src.logging.handlers import get_console_handler

    logger = get_logger("test.handlers.console", level="DEBUG")

    # capture console stream
    stream = StringIO()
    ch = get_console_handler(level="WARNING", stream=stream)

    logger.handlers = []
    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)

    logger.info("this should not appear on console")
    logger.error("this should appear on console")

    lines = []
    for part in stream.getvalue().splitlines():
        if part.strip():
            lines.append(part)

    assert len(lines) >= 1

    # Only ERROR should be present
    messages = []
    for line in lines:
        messages.append(json.loads(line)["message"])

    for msg in messages:
        assert "this should not appear on console" not in msg
    found_error = False
    for msg in messages:
        if "this should appear on console" in msg:
            found_error = True
    assert found_error
