import logging
from pathlib import Path
from typing import Optional, Union


_LOG = logging.getLogger(__name__)


def _to_path(pathlike: Union[str, Path]) -> Path:
    if isinstance(pathlike, Path):
        return pathlike
    return Path(str(pathlike))


def _get_extension_lower(name: str) -> str:
    # Return extension without leading dot, lowercased. Empty string if none.
    idx = -1
    # Find last dot position
    for i in range(len(name) - 1, -1, -1):
        ch = name[i]
        if ch == ".":
            idx = i
            break
    if idx == -1:
        return ""
    if idx == len(name) - 1:
        return ""
    return name[idx + 1 :].lower()


def detect_handler(pathlike: Union[str, Path]) -> Optional[str]:
    """
    Determine handler key from file extension.

    Returns one of: txt, md, docx, xlsx, csv, tsv, pdf, pptx, png, jpeg, svg
    Returns None for unsupported types and logs a skip reason.
    """
    p = _to_path(pathlike)
    name = p.name
    ext = _get_extension_lower(name)

    # Explicit routing without regex, using clear if/elif blocks
    if ext == "txt":
        return "txt"
    elif ext == "md":
        return "md"
    elif ext == "docx":
        return "docx"
    elif ext == "xlsx":
        return "xlsx"
    elif ext == "csv":
        return "csv"
    elif ext == "tsv":
        return "tsv"
    elif ext == "pdf":
        return "pdf"
    elif ext == "pptx":
        return "pptx"
    elif ext == "png":
        return "png"
    elif ext == "jpeg":
        return "jpeg"
    elif ext == "jpg":
        # Normalize to jpeg handler
        return "jpeg"
    elif ext == "svg":
        return "svg"

    # Unknown / unsupported
    _LOG.info("skip: unsupported extension '%s' for file '%s'", ext or "(none)", name)
    return None
