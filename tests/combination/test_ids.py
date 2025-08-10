import os
import tempfile

import pytest

# Target API to be implemented in src/combination/ids.py
# Functional, no OOP, no list comprehensions, no regex.
from src.combination import ids as idmod


def _write(p, name, content):
    path = os.path.join(p, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def _attempt(dir_path, name, tickets_text, checklist_text):
    attempt = os.path.join(dir_path, name)
    os.makedirs(attempt, exist_ok=True)
    _write(attempt, "tickets.md", tickets_text)
    _write(attempt, "checklist.md", checklist_text)
    return attempt


def test_detects_duplicate_ticket_ids_across_attempts():
    # Two attempts with the same ticket ID should be detected as duplicates.
    with tempfile.TemporaryDirectory() as tmp:
        a1 = _attempt(
            tmp,
            "Attempt_A",
            tickets_text=(
                "# Tickets\n\n"
                "- TICKET-101: Alpha work\n"
                "- TICKET-102: Beta work\n"
            ),
            checklist_text=(
                "# Checklist\n\n"
                "- [ ] TICKET-101.01 Do something\n"
            ),
        )
        a2 = _attempt(
            tmp,
            "Attempt_B",
            tickets_text=(
                "# Tickets\n\n"
                "- TICKET-101: Conflicting alpha work\n"
            ),
            checklist_text=(
                "# Checklist\n\n"
                "- [ ] TICKET-200.01 Another thing\n"
            ),
        )

        attempts = [a1, a2]
        index = idmod.build_id_index(attempts)
        dupes = idmod.find_duplicates(index)

        assert "tickets" in dupes
        # Expect TICKET-101 to be duplicated across attempts
        assert "TICKET-101" in dupes["tickets"]
        occ = dupes["tickets"]["TICKET-101"]
        assert isinstance(occ, list)
        assert len(occ) == 2
        # Occurrences should include attempt paths
        paths = [occ[0]["attempt"], occ[1]["attempt"]]
        assert a1 in paths and a2 in paths


def test_detects_duplicate_checklist_task_ids_and_reports_locations():
    # Duplicate checklist task IDs (e.g., TICKET-300.01) across attempts should be detected.
    with tempfile.TemporaryDirectory() as tmp:
        a1 = _attempt(
            tmp,
            "Attempt_X",
            tickets_text=(
                "# Tickets\n\n"
                "- TICKET-300: Work X\n"
            ),
            checklist_text=(
                "# Checklist\n\n"
                "- [ ] TICKET-300.01 First task\n"
                "- [ ] TICKET-300.02 Second task\n"
            ),
        )
        a2 = _attempt(
            tmp,
            "Attempt_Y",
            tickets_text=(
                "# Tickets\n\n"
                "- TICKET-301: Work Y\n"
            ),
            checklist_text=(
                "# Checklist\n\n"
                "- [ ] TICKET-300.01 Duplicate task from another attempt\n"
            ),
        )

        attempts = [a1, a2]
        index = idmod.build_id_index(attempts)
        dupes = idmod.find_duplicates(index)

        assert "checklist" in dupes
        assert "TICKET-300.01" in dupes["checklist"]
        occ = dupes["checklist"]["TICKET-300.01"]
        assert isinstance(occ, list)
        assert len(occ) == 2
        # Each occurrence entry should record attempt path and line number
        assert "attempt" in occ[0] and "line" in occ[0]
        assert "attempt" in occ[1] and "line" in occ[1]
        # Validate attempts present
        paths = [occ[0]["attempt"], occ[1]["attempt"]]
        assert a1 in paths and a2 in paths


def test_index_structure_contains_both_tickets_and_checklist():
    with tempfile.TemporaryDirectory() as tmp:
        a1 = _attempt(
            tmp,
            "Attempt_Z",
            tickets_text=(
                "# Tickets\n\n"
                "- TICKET-500: Something\n"
            ),
            checklist_text=(
                "# Checklist\n\n"
                "- [ ] TICKET-500.01 Task\n"
            ),
        )
        index = idmod.build_id_index([a1])
        assert isinstance(index, dict)
        assert "tickets" in index
        assert "checklist" in index
        # Values are dicts of id -> list of occurrences
        assert isinstance(index["tickets"], dict)
        assert isinstance(index["checklist"], dict)
