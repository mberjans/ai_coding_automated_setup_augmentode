# Minimal mapping writer stub (to be finalized in TICKET-012)
# Functional style, no OOP

from pathlib import Path
from typing import Dict


def capture_paths(original_path: Path, processed_path: Path) -> Dict[str, str]:
    return {
        "original_path": str(original_path),
        "processed_path": str(processed_path),
    }
