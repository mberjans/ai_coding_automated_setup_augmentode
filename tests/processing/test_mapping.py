from pathlib import Path
import json
from typing import Dict

from src.processing import mapping as mp
from src.processing import pipeline as pl


def _read_json(p: Path) -> Dict:
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def test_mapping_append_update_and_error_capture(tmp_path: Path):
    base = tmp_path
    text_dir = base / "processed_documents" / "text"
    text_dir.mkdir(parents=True, exist_ok=True)

    # Create a tiny PNG (not a real image; OCR will be mocked with bytes)
    img = base / "img.png"
    img.write_bytes(b"fake-png-bytes")

    def fake_ocr(data: bytes) -> str:
        return "Hello"

    out1 = pl.run_pipeline_for_path(img, base, ocr_fn=fake_ocr)
    assert out1.get("error") is None
    assert out1.get("ocr_used") is True

    mpath = mp.mapping_path(base)
    assert mpath.exists()
    doc = _read_json(mpath)
    items = doc.get("items", [])
    assert len(items) == 1
    e0 = items[0]
    assert e0.get("source") == str(img)
    assert e0.get("format") == "png"
    assert e0.get("out_path") and Path(e0.get("out_path")).exists()
    with open(e0.get("out_path"), "r", encoding="utf-8") as f:
        assert f.read() == "Hello"

    # Update same file, different OCR result
    def fake_ocr2(data: bytes) -> str:
        return "Hello2"

    out2 = pl.run_pipeline_for_path(img, base, ocr_fn=fake_ocr2)
    assert out2.get("error") is None

    doc2 = _read_json(mpath)
    items2 = doc2.get("items", [])
    assert len(items2) == 1
    e1 = items2[0]
    with open(e1.get("out_path"), "r", encoding="utf-8") as f:
        assert f.read() == "Hello2"

    # Unsupported file should record an error entry and not crash
    unknown = base / "file.bin"
    unknown.write_bytes(b"bin")
    out3 = pl.run_pipeline_for_path(unknown, base)
    assert out3.get("error") is not None

    doc3 = _read_json(mpath)
    items3 = doc3.get("items", [])
    # one for img.png and one for file.bin
    assert len(items3) == 2
    by_source = {}
    for it in items3:
        by_source[it.get("source")] = it
    assert by_source[str(unknown)].get("error") is not None
