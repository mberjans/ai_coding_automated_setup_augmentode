import os
import json
import tempfile

from typing import List


def _write_file(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _make_attempt(tmpdir: str, attempt_name: str, plan: str, tickets: str, checklist: str) -> str:
    ap = os.path.join(tmpdir, attempt_name)
    os.makedirs(ap, exist_ok=True)
    _write_file(os.path.join(ap, "plan.md"), plan)
    _write_file(os.path.join(ap, "tickets.md"), tickets)
    _write_file(os.path.join(ap, "checklist.md"), checklist)
    return ap


def test_engine_produces_combined_docs_and_trace():
    from src.combination import engine

    with tempfile.TemporaryDirectory() as tmp:
        a1 = _make_attempt(tmp, "attempt_A", "Plan A", "Tickets A", "Checklist A")
        a2 = _make_attempt(tmp, "attempt_B", "Plan B", "Tickets B", "Checklist B")

        out_dir = os.path.join(tmp, "COMBINED_RESULTS")
        engine.combine_attempts([a1, a2], out_dir)

        # Combined docs exist
        for name in ("plan.md", "tickets.md", "checklist.md"):
            path = os.path.join(out_dir, name)
            assert os.path.exists(path)
            content = open(path, "r", encoding="utf-8").read()
            assert "Plan" in content or "Tickets" in content or "Checklist" in content
            # Contains simple citation markers
            assert "[source:" in content

        # Trace exists and cites sources
        trace_path = os.path.join(out_dir, "trace.json")
        assert os.path.exists(trace_path)
        with open(trace_path, "r", encoding="utf-8") as f:
            trace = json.load(f)
        # Ensure both attempts are cited for each doc
        for doc in ("plan.md", "tickets.md", "checklist.md"):
            assert doc in trace
            sources: List[str] = trace[doc]
            assert isinstance(sources, list)
            # deterministic include both
            assert a1 in sources
            assert a2 in sources
