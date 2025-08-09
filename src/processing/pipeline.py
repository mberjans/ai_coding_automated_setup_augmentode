from pathlib import Path
from typing import Callable, Dict, Optional

from . import detection
from . import registry
from . import mapping as mp


def _call_parser(fn: Callable, src: Path, base: Path, ocr_fn: Optional[Callable] = None, rasterize_fn: Optional[Callable] = None, ocr_threshold: Optional[int] = None) -> Dict[str, object]:
    # Try calling with the richest signature first, then fall back.
    # Avoid reflection heavy logic; attempt known combinations.
    try:
        if ocr_threshold is not None:
            return fn(src, base, ocr_threshold=ocr_threshold, rasterize_fn=rasterize_fn, ocr_fn=ocr_fn)
    except TypeError:
        pass
    try:
        return fn(src, base, ocr_fn=ocr_fn)
    except TypeError:
        pass
    return fn(src, base)


def run_pipeline_for_path(src_path: Path, base_dir: Path, ocr_fn: Optional[Callable] = None, rasterize_fn: Optional[Callable] = None, ocr_threshold: Optional[int] = None) -> Dict[str, object]:
    p = Path(src_path)
    base = Path(base_dir)
    fmt = detection.detect_handler(p)

    entry: Dict[str, object] = {}
    entry["source"] = str(p)
    entry["format"] = fmt if fmt is not None else ""
    result: Dict[str, object] = {}

    if fmt is None:
        # Unsupported; record error
        msg = "unsupported file type"
        entry["error"] = msg
        mp.upsert_item(base, entry)
        result["error"] = msg
        result["ocr_used"] = False
        return result

    fn = registry.resolve(fmt)
    if fn is None:
        msg = "no parser for format"
        entry["error"] = msg
        mp.upsert_item(base, entry)
        result["error"] = msg
        result["ocr_used"] = False
        return result

    try:
        out = _call_parser(fn, p, base, ocr_fn=ocr_fn, rasterize_fn=rasterize_fn, ocr_threshold=ocr_threshold)
        # success
        entry["out_path"] = out.get("out_path")
        if out.get("ocr_used") is True:
            entry["ocr_used"] = True
        else:
            entry["ocr_used"] = False
        mp.upsert_item(base, entry)
        result = out
        result["error"] = None
        if "ocr_used" not in result:
            result["ocr_used"] = False
        return result
    except Exception as e:
        # Failure; record error entry
        msg = str(e)
        entry["error"] = msg
        mp.upsert_item(base, entry)
        result["error"] = msg
        result["ocr_used"] = False
        return result
