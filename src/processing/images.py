# Image processing helpers for OCR (functional style)
# These are lightweight stubs to avoid external binary deps in core lib.
from pathlib import Path
from typing import List


def rasterize_pdf_to_images(pdf_path: Path) -> List[bytes]:
    """Rasterize PDF pages to image bytes for OCR.

    This default implementation returns an empty list to avoid external binary
    dependencies. Callers can pass a custom rasterize_fn to parse_pdf.
    """
    return []


def preprocess_image_for_ocr(image_bytes: bytes) -> bytes:
    """Optionally preprocess image bytes before OCR.

    No-op placeholder to allow future enhancement.
    """
    return image_bytes
