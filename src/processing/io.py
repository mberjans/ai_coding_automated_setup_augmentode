from pathlib import Path


def ensure_output_dir(base_dir: Path) -> Path:
    out_dir = Path(base_dir) / "processed_documents" / "text"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def write_text_file(path: Path, text: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
