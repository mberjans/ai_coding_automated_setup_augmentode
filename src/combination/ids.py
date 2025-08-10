"""ID normalization and duplicate detection helpers.

Functional only; no OOP, no list comprehensions, no regex.
Parses ticket IDs like 'TICKET-123' and checklist task IDs like 'TICKET-123.01'.
"""
from typing import Any, Dict, List, Tuple
import os


def _read_lines(path: str) -> List[str]:
    lines: List[str] = []
    if not os.path.exists(path):
        return lines
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            lines.append(line.rstrip("\n"))
    return lines


def _find_substring(text: str, sub: str, start: int = 0) -> int:
    i = start
    n = len(text)
    m = len(sub)
    while i <= n - m:
        j = 0
        match = True
        while j < m:
            if text[i + j] != sub[j]:
                match = False
                break
            j = j + 1
        if match:
            return i
        i = i + 1
    return -1


def _is_digit(ch: str) -> bool:
    return ch >= "0" and ch <= "9"


def _parse_ticket_id_from_line(line: str) -> Tuple[bool, str]:
    # Find 'TICKET-'
    idx = _find_substring(line, "TICKET-")
    if idx == -1:
        return False, ""
    i = idx + len("TICKET-")
    # Consume digits
    start = i
    while i < len(line) and _is_digit(line[i]):
        i = i + 1
    if i == start:
        return False, ""
    return True, "TICKET-" + line[start:i]


def _parse_checklist_id_from_line(line: str) -> Tuple[bool, str]:
    # Checklist lines like '- [ ] TICKET-123.01 ...'
    ok, base = _parse_ticket_id_from_line(line)
    if not ok:
        return False, ""
    # Expect a dot then two digits at least
    idx = _find_substring(line, base)
    if idx == -1:
        return False, ""
    i = idx + len(base)
    if i >= len(line) or line[i] != ".":
        return False, ""
    i = i + 1
    start = i
    while i < len(line) and _is_digit(line[i]):
        i = i + 1
    if i == start:
        return False, ""
    return True, base + "." + line[start:i]


def build_id_index(attempt_paths: List[str]) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """Build index: { 'tickets': {id: [ {attempt, line}...] }, 'checklist': {...} }"""
    index: Dict[str, Dict[str, List[Dict[str, Any]]]] = {"tickets": {}, "checklist": {}}
    ai = 0
    while ai < len(attempt_paths):
        attempt = attempt_paths[ai]
        # tickets
        t_lines = _read_lines(os.path.join(attempt, "tickets.md"))
        li = 0
        while li < len(t_lines):
            ok, tid = _parse_ticket_id_from_line(t_lines[li])
            if ok:
                if tid not in index["tickets"]:
                    index["tickets"][tid] = []
                index["tickets"][tid].append({"attempt": attempt, "line": li + 1})
            li = li + 1
        # checklist
        c_lines = _read_lines(os.path.join(attempt, "checklist.md"))
        li = 0
        while li < len(c_lines):
            okc, cid = _parse_checklist_id_from_line(c_lines[li])
            if okc:
                if cid not in index["checklist"]:
                    index["checklist"][cid] = []
                index["checklist"][cid].append({"attempt": attempt, "line": li + 1})
            li = li + 1
        ai = ai + 1
    return index


def find_duplicates(index: Dict[str, Dict[str, List[Dict[str, Any]]]]) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    dupes: Dict[str, Dict[str, List[Dict[str, Any]]]] = {"tickets": {}, "checklist": {}}
    # tickets
    for tid, occ in index.get("tickets", {}).items():
        if len(occ) > 1:
            dupes["tickets"][tid] = occ
    # checklist
    for cid, occ in index.get("checklist", {}).items():
        if len(occ) > 1:
            dupes["checklist"][cid] = occ
    return dupes


def _new_id_with_suffix(original: str, k: int) -> str:
    # Deterministic suffix based on occurrence index starting at 2
    return original + "-ALT" + str(k)


def propose_remap(dupes: Dict[str, Dict[str, List[Dict[str, Any]]]]) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """Return mapping proposals per category and original ID.
    Structure: { 'tickets': { 'TICKET-123': [ {attempt, new_id}, ... for occurrences beyond first ]}, 'checklist': {...} }
    """
    remap: Dict[str, Dict[str, List[Dict[str, Any]]]] = {"tickets": {}, "checklist": {}}
    # tickets
    for tid, occ in dupes.get("tickets", {}).items():
        # skip first occurrence
        mi = 1
        proposals: List[Dict[str, Any]] = []
        while mi < len(occ):
            new_id = _new_id_with_suffix(tid, mi + 1)
            proposals.append({"attempt": occ[mi]["attempt"], "new_id": new_id})
            mi = mi + 1
        remap["tickets"][tid] = proposals
    # checklist
    for cid, occ in dupes.get("checklist", {}).items():
        mi = 1
        proposals_c: List[Dict[str, Any]] = []
        while mi < len(occ):
            new_id = _new_id_with_suffix(cid, mi + 1)
            proposals_c.append({"attempt": occ[mi]["attempt"], "new_id": new_id})
            mi = mi + 1
        remap["checklist"][cid] = proposals_c
    return remap
