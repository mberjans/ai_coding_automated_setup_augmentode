# Parser stubs for text and markdown

from pathlib import Path
from typing import Dict
from ..normalize import utf8_decode_remove_bom, normalize_newlines
from .. import mapping


def _read_bytes(p: Path) -> bytes:
    with open(p, "rb") as f:
        return f.read()


def _ensure_output_dir(base_dir: Path) -> Path:
    out_dir = base_dir / "processed_documents" / "text"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def _write_text_file(path: Path, text: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _md_target_name(src_name: str) -> str:
    # Change .md or .MD to .txt, otherwise append .txt as fallback
    lower = src_name.lower()
    if lower.endswith(".md"):
        return src_name[: -len(".md")] + ".txt"
    return src_name + ".txt"


def parse_txt(src_path: Path, base_dir: Path) -> Dict[str, object]:
    p = Path(src_path)
    base = Path(base_dir)

    raw = _read_bytes(p)
    text = utf8_decode_remove_bom(raw)
    text = normalize_newlines(text)

    out_dir = _ensure_output_dir(base)
    out_path = out_dir / p.name
    _write_text_file(out_path, text)

    map_entry = mapping.capture_paths(p, out_path)
    return {"out_path": str(out_path), "text": text, "mapping": map_entry}


def _strip_md_front_matter(text: str) -> str:
    # Remove initial YAML front-matter delimited by lines containing only '---'
    # Only strip if it appears at the very top of the document.
    lines = text.split("\n")
    if len(lines) == 0:
        return text
    first = lines[0].strip()
    if first != "---":
        return text
    idx = 1
    end_idx = -1
    while idx < len(lines):
        current = lines[idx].strip()
        if current == "---":
            end_idx = idx
            break
        idx = idx + 1
    if end_idx == -1:
        # No closing fence; do not strip
        return text
    # Rebuild without the front-matter block
    remaining_lines = []
    j = end_idx + 1
    while j < len(lines):
        remaining_lines.append(lines[j])
        j = j + 1
    new_text = "\n".join(remaining_lines)
    if not new_text.endswith("\n"):
        new_text = new_text + "\n"
    return new_text


def parse_md(src_path: Path, base_dir: Path) -> Dict[str, object]:
    p = Path(src_path)
    base = Path(base_dir)

    raw = _read_bytes(p)
    text = utf8_decode_remove_bom(raw)
    text = normalize_newlines(text)
    text = _strip_md_front_matter(text)

    out_dir = _ensure_output_dir(base)
    target_name = _md_target_name(p.name)
    out_path = out_dir / target_name
    _write_text_file(out_path, text)
    
    map_entry = mapping.capture_paths(p, out_path)
    return {"out_path": str(out_path), "text": text, "mapping": map_entry}
