from pathlib import Path
from PIL import Image, ImageDraw


def _make_blank_png(path: Path, size=(100, 40)):
    img = Image.new("RGB", size, color=(255, 255, 255))
    img.save(path, format="PNG")


def _make_blank_jpeg(path: Path, size=(100, 40)):
    img = Image.new("RGB", size, color=(255, 255, 255))
    img.save(path, format="JPEG")


def _make_svg(path: Path, texts):
    # simple svg with text nodes
    parts = [
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
        "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"200\" height=\"100\">",
    ]
    i = 0
    while i < len(texts):
        parts.append(f"<text x=\"10\" y=\"{20 + i*20}\">{texts[i]}</text>")
        i += 1
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def test_image_png_ocr_with_monkeypatch(tmp_path: Path):
    from src.processing.parsers import image_svg

    src = tmp_path / "sample.png"
    _make_blank_png(src)

    def fake_ocr(img_bytes: bytes):
        return "HELLO OCR"

    out = image_svg.parse_image(src, tmp_path, ocr_fn=fake_ocr)

    assert isinstance(out, dict)
    assert out.get("ocr_used") is True
    assert "HELLO OCR" in out.get("text", "")
    assert str(out.get("out_path")).endswith(str(Path("processed_documents") / "text" / "sample.txt"))


def test_image_jpeg_no_ocr_returns_empty(tmp_path: Path):
    from src.processing.parsers import image_svg

    src = tmp_path / "photo.jpg"
    _make_blank_jpeg(src)

    out = image_svg.parse_image(src, tmp_path)

    assert out.get("ocr_used") is False
    assert out.get("text") == ""


def test_svg_text_extraction(tmp_path: Path):
    from src.processing.parsers import image_svg

    src = tmp_path / "vector.svg"
    _make_svg(src, ["Alpha", "Beta"]) 

    out = image_svg.parse_svg(src, tmp_path)

    assert "Alpha" in out.get("text", "")
    assert "Beta" in out.get("text", "")
    assert out.get("ocr_used") is False
    assert str(out.get("out_path")).endswith(str(Path("processed_documents") / "text" / "vector.txt"))
