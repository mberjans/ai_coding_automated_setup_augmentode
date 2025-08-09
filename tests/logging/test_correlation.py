"""
Failing tests for per-run correlation ID (TICKET-003.04).
"""
import json
import logging
from io import StringIO

from src.logging.json_logger import get_logger


def test_correlation_id_present_and_stable_in_session():
    logger = get_logger("test.correlation", level="DEBUG")

    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger.handlers = []
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    logger.info("first")
    logger.debug("second")

    lines = []
    for part in stream.getvalue().splitlines():
        if part.strip():
            lines.append(part)

    assert len(lines) >= 2
    rec1 = json.loads(lines[0])
    rec2 = json.loads(lines[1])

    assert "correlation_id" in rec1
    assert "correlation_id" in rec2
    assert rec1["correlation_id"] == rec2["correlation_id"]
