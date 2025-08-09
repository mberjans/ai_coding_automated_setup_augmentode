"""
Tests for path helper functions (TICKET-004.04).
"""
from pathlib import Path


def test_sanitize_folder_name_public_wrapper():
    from src.paths.manager import sanitize_folder_name

    assert sanitize_folder_name("Okay-Name_1.0") == "Okay-Name_1.0"
    assert sanitize_folder_name("Bad*Name?") == "Bad_Name_"
    assert sanitize_folder_name("Slash/Back\\Colon:") == "Slash_Back_Colon_"
    assert sanitize_folder_name("Space name") == "Space_name"


def test_join_paths_public_helper():
    from src.paths.manager import join_paths

    base = "/tmp"
    p = join_paths(base, "A", "B", "C")
    assert p.endswith(str(Path("A") / "B" / "C"))

    p2 = join_paths(base, "A", "", "C")
    assert p2.endswith(str(Path("A") / "C"))
