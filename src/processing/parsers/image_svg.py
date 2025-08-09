# Image (PNG/JPEG) OCR and SVG text extraction parsers
from pathlib import Path
from typing import Callable, Dict, Optional

from ..io import ensure_output_dir, write_text_file
from ..normalize import normalize_newlines, remove_control_chars


def parse_image(src_path: Path, base_dir: Path, ocr_fn: Optional[Callable[[bytes], str]] = None) -> Dict[str, object]:
    p = Path(src_path)
    base = Path(base_dir)
    try:
        data = p.read_bytes()
    except Exception:
        data = b""

    text = ""
    ocr_used = False
    if ocr_fn is not None:
        try:
            text = ocr_fn(data) or ""
        except Exception:
            text = ""
        ocr_used = True if len((text or "").strip()) > 0 else False

    text = normalize_newlines(text)
    text = remove_control_chars(text)
    # Coerce whitespace-only to empty string for deterministic output
    if len(text.strip()) == 0:
        text = ""

    out_dir = ensure_output_dir(base)
    out_path = out_dir / (p.stem + ".txt")
    write_text_file(out_path, text)

    result: Dict[str, object] = {}
    result["out_path"] = str(out_path)
    result["text"] = text
    result["ocr_used"] = ocr_used
    return result


def parse_svg(src_path: Path, base_dir: Path) -> Dict[str, object]:
    # Use ElementTree to extract <text> nodes
    p = Path(src_path)
    base = Path(base_dir)
    try:
        import xml.etree.ElementTree as ET
    except Exception as e:
        raise RuntimeError(f"XML parser required: {e}")

    try:
        tree = ET.parse(str(p))
        root = tree.getroot()
    except Exception:
        # Malformed SVG → empty output
        root = None

    lines = []
    if root is not None:
        # Traverse elements and collect text where tag endswith 'text'
        for elem in root.iter():
            tag = elem.tag
            # handle namespaces by checking suffix
            suffix = "text"
            if isinstance(tag, str):
                if tag.endswith(suffix):
                    t = elem.text or ""
                    if len(t) > 0:
                        lines.append(t)

    text = "\n".join(lines)
    text = normalize_newlines(text)
    text = remove_control_chars(text)

    out_dir = ensure_output_dir(base)
    out_path = out_dir / (p.stem + ".txt")
    write_text_file(out_path, text)

    result: Dict[str, object] = {}
    result["out_path"] = str(out_path)
    result["text"] = text
    result["ocr_used"] = False
    return result
