# PDF parser with optional OCR fallback (functional style)
from pathlib import Path
from typing import Callable, Dict, List, Optional

from ..io import ensure_output_dir, write_text_file
from ..normalize import normalize_newlines, remove_control_chars


def _extract_text_pypdf(pdf_path: Path) -> List[str]:
    pages: List[str] = []
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception as e:
        raise RuntimeError(f"pypdf is required for PDF parsing: {e}")

    reader = PdfReader(str(pdf_path))
    i = 0
    while i < len(reader.pages):
        page = reader.pages[i]
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        pages.append(text)
        i = i + 1
    return pages


def parse_pdf(
    src_path: Path,
    base_dir: Path,
    ocr_threshold: int = 10,
    rasterize_fn: Optional[Callable[[Path], List[bytes]]] = None,
    ocr_fn: Optional[Callable[[bytes], str]] = None,
) -> Dict[str, object]:
    p = Path(src_path)
    base = Path(base_dir)

    # Extract searchable text
    pages = _extract_text_pypdf(p)
    combined = "\n".join(pages)
    combined = normalize_newlines(combined)
    combined = remove_control_chars(combined)

    ocr_used = False

    # OCR fallback if text yield is too low and hooks provided
    if len(combined.strip()) < int(ocr_threshold):
        # Provide default rasterizer if not supplied
        if rasterize_fn is None:
            try:
                from ..images import rasterize_pdf_to_images  # type: ignore
                rasterize_fn = rasterize_pdf_to_images
            except Exception:
                rasterize_fn = None
        if rasterize_fn is not None and ocr_fn is not None:
            try:
                images = rasterize_fn(p)
            except Exception:
                images = []
            ocr_texts: List[str] = []
            j = 0
            while j < len(images):
                try:
                    t = ocr_fn(images[j])
                except Exception:
                    t = ""
                ocr_texts.append(t)
                j = j + 1
            ocr_combined = "\n".join(ocr_texts)
            ocr_combined = normalize_newlines(ocr_combined)
            ocr_combined = remove_control_chars(ocr_combined)
            # Only mark OCR used if we actually obtained any non-empty text
            if len(ocr_combined.strip()) > 0:
                combined = ocr_combined
                ocr_used = True

    out_dir = ensure_output_dir(base)
    out_path = out_dir / (p.stem + ".txt")
    write_text_file(out_path, combined)

    result: Dict[str, object] = {}
    result["out_path"] = str(out_path)
    result["text"] = combined
    result["pages"] = max(1, len(pages))
    result["ocr_used"] = ocr_used
    return result
