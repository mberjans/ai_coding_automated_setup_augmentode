from pathlib import Path

import io
import os
import pytest


def _write_text(path: Path, text: str, add_bom: bool = False):
    data = text.encode("utf-8")
    if add_bom:
        data = b"\xef\xbb\xbf" + data
    with open(path, "wb") as f:
        f.write(data)


# TICKET-006.01: Failing tests for reading .txt/.md, UTF-8 normalization (BOM + newlines),
# and output path under processed_documents/text/.

def test_parse_txt_writes_normalized_output(tmp_path: Path):
    from src.processing.parsers import txt_md

    src = tmp_path / "note.txt"
    _write_text(src, "Hello\r\nWorld\rGoodbye\n")

    out = txt_md.parse_txt(src, tmp_path)

    # Validate structure
    assert isinstance(out, dict)
    assert "out_path" in out
    assert "text" in out

    out_path = out["out_path"]
    assert str(out_path).endswith(os.path.join("processed_documents", "text", "note.txt"))

    # File exists and has normalized newlines
    text = out["text"]
    assert "\r" not in text
    assert text == "Hello\nWorld\nGoodbye\n"

    written = Path(out_path).read_text(encoding="utf-8")
    assert written == text


def test_parse_md_bom_removed_and_writes_txt_output(tmp_path: Path):
    from src.processing.parsers import txt_md

    src = tmp_path / "README.md"
    _write_text(src, "# Title\r\n\nContent", add_bom=True)

    out = txt_md.parse_md(src, tmp_path)

    out_path = out["out_path"]
    # Markdown should be saved as .txt under processed_documents/text/
    assert str(out_path).endswith(os.path.join("processed_documents", "text", "README.txt"))

    # No BOM present and newlines normalized
    text = out["text"]
    assert text.startswith("# Title\n")
    assert "\r" not in text

    written = Path(out_path).read_text(encoding="utf-8")
    assert written == text
