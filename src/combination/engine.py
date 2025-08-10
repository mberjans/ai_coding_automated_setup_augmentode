"""Combination Strategy Engine (functional).

Produces combined plan/tickets/checklist with simple source citations and a trace.json
mapping each output doc to its source attempt paths.

Constraints: functional style, no OOP, no list comprehensions, no regex.
"""
import json
import os
from typing import Dict, List


def _read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def _write_text(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _combine_one(attempt_paths: List[str], filename: str) -> str:
    combined = []
    i = 0
    while i < len(attempt_paths):
        ap = attempt_paths[i]
        part_path = os.path.join(ap, filename)
        text = _read_file(part_path)
        if len(text) > 0:
            # Add a simple citation header per section
            combined.append(f"[source: {ap}]\n")
            combined.append(text)
            if not text.endswith("\n"):
                combined.append("\n")
            combined.append("\n")
        i = i + 1
    return "".join(combined)


def _build_trace(attempt_paths: List[str]) -> Dict[str, List[str]]:
    trace: Dict[str, List[str]] = {}
    docs = ["plan.md", "tickets.md", "checklist.md"]
    di = 0
    while di < len(docs):
        name = docs[di]
        # Copy attempt paths deterministically
        sources: List[str] = []
        i = 0
        while i < len(attempt_paths):
            sources.append(attempt_paths[i])
            i = i + 1
        trace[name] = sources
        di = di + 1
    return trace


def combine_attempts(attempt_paths: List[str], out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    # Combine each document
    plan = _combine_one(attempt_paths, "plan.md")
    tickets = _combine_one(attempt_paths, "tickets.md")
    checklist = _combine_one(attempt_paths, "checklist.md")

    _write_text(os.path.join(out_dir, "plan.md"), plan)
    _write_text(os.path.join(out_dir, "tickets.md"), tickets)
    _write_text(os.path.join(out_dir, "checklist.md"), checklist)

    # Trace
    trace = _build_trace(attempt_paths)
    with open(os.path.join(out_dir, "trace.json"), "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2, ensure_ascii=False)
