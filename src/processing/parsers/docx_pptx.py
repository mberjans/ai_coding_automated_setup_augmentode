# Parsers for Office documents (functional style)

from pathlib import Path
from typing import Dict, List
import zipfile

from ..normalize import normalize_newlines, utf8_decode_remove_bom
from .. import mapping


def _ensure_output_dir(base_dir: Path) -> Path:
    out_dir = base_dir / "processed_documents" / "text"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def _write_text_file(path: Path, text: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _extract_all_between(s: str, start: str, end: str) -> List[str]:
    # Simple scanning without regex
    results = []
    idx = 0
    while True:
        i = s.find(start, idx)
        if i == -1:
            break
        j = s.find(end, i + len(start))
        if j == -1:
            break
        results.append(s[i + len(start) : j])
        idx = j + len(end)
    return results


def parse_docx(src_path: Path, base_dir: Path) -> Dict[str, object]:
    p = Path(src_path)
    base = Path(base_dir)

    paragraphs: List[str] = []
    with zipfile.ZipFile(p, "r") as z:
        # Minimal required part for tests
        xml_bytes = z.read("word/document.xml")
        xml = utf8_decode_remove_bom(xml_bytes)
        # Extract text nodes
        texts = _extract_all_between(xml, "<w:t>", "</w:t>")
        for t in texts:
            paragraphs.append(t)

    # Join as lines and normalize
    text = "\n".join(paragraphs)
    text = normalize_newlines(text)

    out_dir = _ensure_output_dir(base)
    out_name = p.stem + ".txt"
    out_path = out_dir / out_name
    _write_text_file(out_path, text)

    map_entry = mapping.capture_paths(p, out_path)
    return {"out_path": str(out_path), "text": text, "mapping": map_entry}


def _slide_index_from_name(name: str) -> int:
    # name like 'ppt/slides/slideN.xml' → return N
    # Parse digits after last 'slide'
    idx = name.rfind("slide")
    if idx == -1:
        return 0
    i = idx + len("slide")
    n = 0
    found = False
    while i < len(name):
        ch = name[i]
        if ch >= "0" and ch <= "9":
            found = True
            n = n * 10 + (ord(ch) - ord("0"))
            i = i + 1
            continue
        break
    if not found:
        return 0
    return n


def parse_pptx(src_path: Path, base_dir: Path) -> Dict[str, object]:
    p = Path(src_path)
    base = Path(base_dir)

    slides_texts: List[str] = []
    with zipfile.ZipFile(p, "r") as z:
        names = []
        for name in z.namelist():
            if name.startswith("ppt/slides/slide") and name.endswith(".xml"):
                names.append(name)
        # Sort by slide index
        # Simple selection sort without list comprehensions
        ordered = []
        while len(names) > 0:
            best_idx = 0
            k = 1
            while k < len(names):
                if _slide_index_from_name(names[k]) < _slide_index_from_name(names[best_idx]):
                    best_idx = k
                k = k + 1
            ordered.append(names[best_idx])
            del names[best_idx]

        # Extract text from each slide
        si = 0
        while si < len(ordered):
            name = ordered[si]
            xml_bytes = z.read(name)
            xml = utf8_decode_remove_bom(xml_bytes)
            texts = _extract_all_between(xml, "<a:t>", "</a:t>")
            # Join texts within a slide by newline
            slide_text = "\n".join(texts)
            slide_text = normalize_newlines(slide_text)
            slides_texts.append(slide_text.rstrip("\n"))
            si = si + 1

    # Join slides with separator line
    combined = "\n---\n".join(slides_texts)
    text = normalize_newlines(combined)

    out_dir = _ensure_output_dir(base)
    out_name = p.stem + ".txt"
    out_path = out_dir / out_name
    _write_text_file(out_path, text)

    map_entry = mapping.capture_paths(p, out_path)
    return {"out_path": str(out_path), "text": text, "mapping": map_entry}
