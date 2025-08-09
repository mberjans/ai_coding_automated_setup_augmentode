from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


def _make_text_pdf(path: Path, lines):
    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    y = height - 72
    i = 0
    while i < len(lines):
        c.drawString(72, y, lines[i])
        y -= 14
        i += 1
    c.showPage()
    c.save()


def test_pdf_searchable_text_extraction(tmp_path: Path):
    from src.processing.parsers import pdf

    src = tmp_path / "searchable.pdf"
    _make_text_pdf(src, ["Hello", "World"]) 

    out = pdf.parse_pdf(src, tmp_path)

    assert isinstance(out, dict)
    assert "out_path" in out and "text" in out and "pages" in out
    assert str(out["out_path"]).endswith(str(Path("processed_documents") / "text" / "searchable.txt"))
    assert "Hello" in out["text"]
    assert out.get("ocr_used") is False
    assert out["pages"] >= 1


def test_pdf_ocr_fallback_when_low_yield(tmp_path: Path, monkeypatch):
    from src.processing.parsers import pdf

    src = tmp_path / "image_only.pdf"
    # create an empty text PDF (no text) so initial extraction yields nothing
    _make_text_pdf(src, [])

    def fake_rasterize(_path):
        # return a list of page placeholders for OCR
        return [b"<page1>"]

    def fake_ocr(_image_bytes):
        return "OCR_TEXT"

    out = pdf.parse_pdf(src, tmp_path, ocr_threshold=5, rasterize_fn=fake_rasterize, ocr_fn=fake_ocr)

    assert "OCR_TEXT" in out["text"]
    assert out.get("ocr_used") is True


def test_pdf_no_ocr_when_threshold_met(tmp_path: Path):
    from src.processing.parsers import pdf

    src = tmp_path / "enough_text.pdf"
    # Create a PDF with sufficient text content
    _make_text_pdf(src, ["This is enough text to exceed threshold.", "Another line."])

    def never_called(_img):
        raise AssertionError("OCR should not be called when threshold is met")

    out = pdf.parse_pdf(src, tmp_path, ocr_threshold=5, rasterize_fn=lambda p: [b"x"], ocr_fn=never_called)
    assert out.get("ocr_used") is False
    assert "enough" in out["text"].lower()


def test_pdf_missing_tesseract_binary_is_handled(tmp_path: Path):
    from src.processing.parsers import pdf

    src = tmp_path / "needs_ocr.pdf"
    # Produce virtually no text so OCR would be considered
    _make_text_pdf(src, [])

    def missing_tesseract(_path: Path):
        # Simulate system missing OCR/rasterization dependency
        raise FileNotFoundError("tesseract not found")

    # Even though rasterize fails, parser should not crash and should not mark ocr_used
    out = pdf.parse_pdf(src, tmp_path, ocr_threshold=10, rasterize_fn=missing_tesseract, ocr_fn=lambda b: "should not run")
    assert out.get("ocr_used") is False
