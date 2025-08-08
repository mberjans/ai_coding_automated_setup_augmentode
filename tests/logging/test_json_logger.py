"""
Failing tests for JSON logger (TICKET-003.01).

Asserts:
- emitted records are JSON with expected keys
- log level is respected
- API keys and secrets are redacted from messages
"""

import json
import logging
from io import StringIO
import os


def _capture_logger_stream(name: str, level: str):
    # Returns (logger, stream, handler) so caller can inspect and cleanup
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger = logging.getLogger(name)
    logger.handlers = []
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, level))
    return logger, stream, handler


def test_json_structure_and_levels():
    # Import target factory
    from src.logging.json_logger import get_logger

    # get JSON logger
    logger = get_logger("test.json", level="INFO")

    # Attach memory stream to capture output
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger.handlers = []
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    logger.info("hello world")

    output = stream.getvalue().strip()
    assert output, "no output captured"

    # must be valid JSON
    record = json.loads(output)
    # expected keys
    assert "level" in record
    assert "message" in record
    assert "name" in record
    # level respected
    assert record["level"] == "INFO"
    assert record["message"] == "hello world"
    assert record["name"] == "test.json"


def test_redaction_of_api_keys_and_env_names():
    from src.logging.json_logger import get_logger

    logger = get_logger("test.redaction", level="DEBUG")
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger.handlers = []
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    # Set env var and craft messages that could expose secrets
    os.environ["MY_SECRET_API_KEY"] = "top-secret-12345"

    try:
        # include both key-like fragments and env var names
        logger.debug("auth key=top-secret-12345 provided via MY_SECRET_API_KEY")
        logger.info("Using MY_SECRET_API_KEY to authenticate")

        # build non-empty lines without list comprehension
        lines = []
        for part in stream.getvalue().splitlines():
            if part.strip():
                lines.append(part)
        assert len(lines) >= 2

        # decode messages without list comprehension
        redacted = []
        for line in lines:
            redacted.append(json.loads(line)["message"])

        # ensure raw secret and env var name not present
        for msg in redacted:
            assert "top-secret-12345" not in msg
            assert "MY_SECRET_API_KEY" not in msg
            # allow presence of placeholder
            assert "[REDACTED]" in msg
    finally:
        if "MY_SECRET_API_KEY" in os.environ:
            del os.environ["MY_SECRET_API_KEY"]
