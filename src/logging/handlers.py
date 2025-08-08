"""
Logging handlers for JSON logger (TICKET-003.02/003.04 partial).

- get_file_handler(file_path): returns a RotatingFileHandler pointing to file_path.
- get_console_handler(level, stream): returns a StreamHandler bound to provided stream with specified level.

Handlers intentionally use a simple formatter of "%(message)s" so that the
JSON already injected by the LogRecordFactory is emitted verbatim.
"""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, TextIO


_DEF_MAX_BYTES = 1_000_000
_DEF_BACKUP_COUNT = 3


def _ensure_parent_dir(path_str: str) -> None:
    p = Path(path_str)
    parent = p.parent
    if not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)


def _basic_json_formatter() -> logging.Formatter:
    # keep only the message, which is already JSON
    return logging.Formatter("%(message)s")


def get_file_handler(file_path: str,
                     max_bytes: int = _DEF_MAX_BYTES,
                     backup_count: int = _DEF_BACKUP_COUNT) -> logging.Handler:
    """Create a rotating file handler that writes JSON lines to file_path."""
    _ensure_parent_dir(file_path)
    handler = RotatingFileHandler(filename=file_path,
                                  maxBytes=max_bytes,
                                  backupCount=backup_count)
    handler.setFormatter(_basic_json_formatter())
    return handler


def _level_from_string(level: str) -> int:
    if not level:
        return logging.INFO
    name = str(level).upper()
    if name == "CRITICAL":
        return logging.CRITICAL
    if name == "ERROR":
        return logging.ERROR
    if name == "WARNING":
        return logging.WARNING
    if name == "INFO":
        return logging.INFO
    if name == "DEBUG":
        return logging.DEBUG
    return logging.INFO


def get_console_handler(level: str = "INFO", stream: Optional[TextIO] = None) -> logging.Handler:
    """Create a console StreamHandler with the given minimum level and stream."""
    handler = logging.StreamHandler(stream)
    handler.setLevel(_level_from_string(level))
    handler.setFormatter(_basic_json_formatter())
    return handler
