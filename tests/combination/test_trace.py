import os
import json
import tempfile

from src.combination import trace


def test_trace_with_rationale_written_and_has_per_doc_entries():
    # Two fake attempt paths
    attempts = [
        "/tmp/attempt_X",
        "/tmp/attempt_Y",
    ]

    t = trace.build_trace_with_rationale(attempts)
    # Expect docs as keys, values are list of {path, rationale}
    for doc in ("plan.md", "tickets.md", "checklist.md"):
        assert doc in t
        entries = t[doc]
        assert isinstance(entries, list)
        assert len(entries) == 2
        assert entries[0]["path"] == attempts[0]
        assert isinstance(entries[0]["rationale"], str)

    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "COMBINED_RESULTS")
        trace.write_trace(out, t)
        path = os.path.join(out, "trace.json")
        assert os.path.exists(path)
        data = json.load(open(path, "r", encoding="utf-8"))
        assert "plan.md" in data
        assert isinstance(data["plan.md"], list)
        assert data["plan.md"][0]["path"] == attempts[0]
