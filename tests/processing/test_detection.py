import os
from pathlib import Path

import pytest

# TICKET-005.01: Failing tests for format detection and routing
# Expected mapping from file extension to handler key
KNOWN_CASES = [
    ("note.txt", "txt"),
    ("README.md", "md"),
    ("doc.DOCX", "docx"),
    ("table.xlsx", "xlsx"),
    ("data.csv", "csv"),
    ("data.tsv", "tsv"),
    ("paper.pdf", "pdf"),
    ("slides.pptx", "pptx"),
    ("image.png", "png"),
    ("photo.jpeg", "jpeg"),
    ("vector.svg", "svg"),
]


@pytest.mark.parametrize("filename, expected", KNOWN_CASES)
def test_detect_handler_from_path_string(filename, expected):
    # Import inside test to avoid import errors preventing collection of other tests
    from src.processing import detection

    path_str = os.path.join("/tmp", filename)
    result = detection.detect_handler(path_str)
    assert result == expected


@pytest.mark.parametrize("filename, expected", KNOWN_CASES)
def test_detect_handler_from_path_object(filename, expected):
    from src.processing import detection

    path_obj = Path("/tmp") / filename
    result = detection.detect_handler(path_obj)
    assert result == expected
