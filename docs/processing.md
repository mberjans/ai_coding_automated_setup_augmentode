# Document Processing Overview

This project routes input files to parsers based on extension using explicit, readable logic (no regex).

## Supported Formats

The detection module `src/processing/detection.py` returns a handler key for each supported type:

- txt → plain text parser
- md → Markdown parser
- docx → Microsoft Word
- xlsx → Microsoft Excel
- csv → Comma-separated values
- tsv → Tab-separated values
- pdf → Portable Document Format
- pptx → Microsoft PowerPoint
- png → Portable Network Graphics
- jpeg → JPEG images (includes .jpg)
- svg → Scalable Vector Graphics

Unknown or unsupported extensions are skipped. A log entry at INFO level is emitted in the form:

```
skip: unsupported extension '<ext>' for file '<name>'
```

## Registry

The registry in `src/processing/registry.py` maps handler keys to parser callables in `src/processing/parsers/`.
It provides two helpers:

- `get_registry()` → returns the mapping dict
- `resolve(fmt)` → returns a callable or `None` if not found

## Parsers Overview

- `src/processing/parsers/pdf.py` extracts searchable text via pypdf and supports an OCR fallback when text yield is below a threshold. Callers can pass `rasterize_fn` and `ocr_fn` to avoid external binary dependencies in tests. Outputs go to `processed_documents/text/<name>.txt`.

- `src/processing/parsers/image_svg.py` provides:
  - `parse_image(path, base_dir, ocr_fn=None)` which reads image bytes and, if `ocr_fn` is provided, uses it to extract text. Normalization removes control characters and enforces newline policy. When OCR produces only whitespace, the output is coerced to an empty string. Writes to `processed_documents/text/<name>.txt`.
  - `parse_svg(path, base_dir)` which parses `<text>` nodes using ElementTree without regex, joining them with newlines and writing normalized text to `processed_documents/text/<name>.txt`.

## OCR Configuration

- OCR is injected via callables to keep the core library free from hard dependencies on OCR engines:
  - For PDFs: `parse_pdf(..., rasterize_fn=..., ocr_fn=...)`.
  - For images: `parse_image(..., ocr_fn=...)`.
- The default rasterizer helper is in `src/processing/images.py` and returns an empty list to avoid shelling out by default. Projects can plug a real rasterizer or pre-processing function as needed.

## Next Steps

- Continue extending parsers and pipeline per tickets. Ensure outputs are deterministic and normalized.
