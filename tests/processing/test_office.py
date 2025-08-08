from pathlib import Path
import os
import zipfile
import io
import pytest


def _mk_minimal_docx(path: Path, paragraphs):
    # Create a minimal DOCX-like zip with only word/document.xml
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        # Build document.xml with given paragraphs
        # Use w namespace but parser will not depend on exact URI
        head = (
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
            "<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\">"
            "<w:body>"
        )
        body = ""
        for p in paragraphs:
            body += "<w:p><w:r><w:t>" + p + "</w:t></w:r></w:p>"
        tail = "</w:body></w:document>"
        xml = head + body + tail
        z.writestr("word/document.xml", xml)
    with open(path, "wb") as f:
        f.write(buf.getvalue())


ess_slides = None

def _mk_minimal_pptx(path: Path, slides):
    # Create a minimal PPTX-like zip with ppt/slides/slideN.xml files
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        idx = 1
        for slide in slides:
            # slide is list of text chunks; put them into <a:t>
            xml = (
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
                "<p:sld xmlns:p=\"http://schemas.openxmlformats.org/presentationml/2006/main\" "
                "xmlns:a=\"http://schemas.openxmlformats.org/drawingml/2006/main\">"
                "<p:cSld><p:spTree>"
            )
            for t in slide:
                xml += "<p:sp><p:txBody><a:p><a:r><a:t>" + t + "</a:t></a:r></a:p></p:txBody></p:sp>"
            xml += "</p:spTree></p:cSld></p:sld>"
            z.writestr(f"ppt/slides/slide{idx}.xml", xml)
            idx += 1
    with open(path, "wb") as f:
        f.write(buf.getvalue())


# TICKET-007.01: Failing tests for docx paragraph extraction and pptx slide separation markers.

def test_parse_docx_extracts_paragraphs_and_writes_output(tmp_path: Path):
    from src.processing.parsers import docx_pptx

    src = tmp_path / "sample.docx"
    _mk_minimal_docx(src, ["Hello", "World"]) 

    out = docx_pptx.parse_docx(src, tmp_path)

    assert isinstance(out, dict)
    assert "out_path" in out
    assert "text" in out
    assert "mapping" in out

    out_path = out["out_path"]
    assert str(out_path).endswith(os.path.join("processed_documents", "text", "sample.txt"))

    text = out["text"]
    assert text == "Hello\nWorld\n"


def test_parse_pptx_extracts_slides_with_separators(tmp_path: Path):
    from src.processing.parsers import docx_pptx

    src = tmp_path / "deck.pptx"
    _mk_minimal_pptx(src, [["Title", "First slide"], ["Second"]])

    out = docx_pptx.parse_pptx(src, tmp_path)
    out_path = out["out_path"]
    assert str(out_path).endswith(os.path.join("processed_documents", "text", "deck.txt"))

    text = out["text"]
    # Should contain both slides' text and a separator line '---' between them
    assert "Title" in text
    assert "First slide" in text
    assert "Second" in text
    assert "\n---\n" in text
