"""
Structured JSON logger with redaction (TICKET-003).

Provides get_logger(name, level) that returns a standard logging.Logger.
Messages are transformed at record creation time into JSON with keys:
- level
- message (with secrets redacted)
- name

Redaction rules (no regex):
- Replace any environment variable name found in the message with "[REDACTED]".
- Replace any environment variable value found in the message with "[REDACTED]".
- Replace any substring after "key=" up to the next space (or end) with "[REDACTED]".

This uses logging.setLogRecordFactory so that even when tests attach their own
handlers without a JSON formatter, the emitted record message is already JSON.
"""
from __future__ import annotations

import json
import logging
import os
import uuid
from typing import Callable, Optional


_ORIGINAL_FACTORY = logging.getLogRecordFactory()
_FACTORY_INSTALLED = False
_RUN_CORRELATION_ID = uuid.uuid4().hex


def _starts_with_at(s: str, idx: int, prefix: str) -> bool:
    if idx < 0:
        return False
    if idx + len(prefix) > len(s):
        return False
    return s[idx: idx + len(prefix)] == prefix


def _replace_substring_range(s: str, start: int, end: int, replacement: str) -> str:
    # end is exclusive
    return s[:start] + replacement + s[end:]


def _redact_key_equals(message: str) -> str:
    # Scan for occurrences of "key=" and redact following token until space or end
    i = 0
    target = "key="
    while True:
        idx = message.find(target, i)
        if idx == -1:
            break
        # position after "key="
        start_secret = idx + len(target)
        j = start_secret
        # advance until space or end
        while j < len(message) and message[j] != " ":
            j += 1
        message = _replace_substring_range(message, start_secret, j, "[REDACTED]")
        i = j
    return message


def _redact_env_names_and_values(message: str) -> str:
    # Redact env variable names and their values if present in the message
    # Avoid list comprehensions as per project rules.
    for name, value in os.environ.items():
        if name and name in message:
            message = message.replace(name, "[REDACTED]")
        if value and isinstance(value, str) and value in message:
            message = message.replace(value, "[REDACTED]")
    return message


def _redact_message(message: str) -> str:
    if not message:
        return message
    msg = message
    msg = _redact_env_names_and_values(msg)
    msg = _redact_key_equals(msg)
    return msg


def _install_factory_once() -> None:
    global _FACTORY_INSTALLED
    if _FACTORY_INSTALLED:
        return

    original = _ORIGINAL_FACTORY

    def factory(*args, **kwargs):
        record = original(*args, **kwargs)
        # Build JSON payload and replace msg so any handler outputs JSON
        try:
            msg = record.getMessage()
        except Exception:
            msg = str(record.msg)
        msg = _redact_message(msg)
        payload = {
            "level": record.levelname,
            "message": msg,
            "name": record.name,
            "correlation_id": _RUN_CORRELATION_ID,
        }
        record.msg = json.dumps(payload, ensure_ascii=False)
        record.args = ()
        return record

    logging.setLogRecordFactory(factory)
    _FACTORY_INSTALLED = True


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Return a standard Logger that emits JSON-encoded records with redaction.

    The returned logger has no handlers configured; callers can attach their own
    handlers as needed. Level is applied to the logger.
    """
    _install_factory_once()
    logger = logging.getLogger(name)
    # do not mutate handlers; the caller/tests will attach their own
    level_value = getattr(logging, str(level).upper(), logging.INFO)
    logger.setLevel(level_value)
    return logger
