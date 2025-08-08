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

## Next Steps

- Implement text and Markdown parsers with normalization and safe output paths in `processed_documents/text/`.
- Build parsers for Office, tabular, PDFs (with OCR fallback), images, and SVG per tickets.
