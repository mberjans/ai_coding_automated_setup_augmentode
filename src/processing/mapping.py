# Mapping writer for processed_documents/mapping.json
from pathlib import Path
from typing import Dict, List
import json


def mapping_path(base_dir: Path) -> Path:
    d = Path(base_dir) / "processed_documents"
    d.mkdir(parents=True, exist_ok=True)
    return d / "mapping.json"


def _empty_doc() -> Dict[str, object]:
    return {"items": []}


def read_mapping(base_dir: Path) -> Dict[str, object]:
    mp = mapping_path(base_dir)
    if not mp.exists():
        return _empty_doc()
    try:
        with open(mp, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return _empty_doc()


def write_mapping(base_dir: Path, doc: Dict[str, object]) -> None:
    mp = mapping_path(base_dir)
    tmp = mp.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    tmp.replace(mp)


def upsert_item(base_dir: Path, entry: Dict[str, object]) -> None:
    doc = read_mapping(base_dir)
    items = doc.get("items")
    if not isinstance(items, list):
        items = []
    # find by source
    src = entry.get("source")
    found = -1
    i = 0
    while i < len(items):
        it = items[i]
        if isinstance(it, dict) and it.get("source") == src:
            found = i
            break
        i = i + 1
    if found >= 0:
        items[found] = entry
    else:
        items.append(entry)
    doc["items"] = items
    write_mapping(base_dir, doc)


def capture_paths(original_path: Path, processed_path: Path) -> Dict[str, str]:
    # Compatibility helper used by some parsers' tests
    return {
        "source": str(original_path),
        "out_path": str(processed_path),
    }
