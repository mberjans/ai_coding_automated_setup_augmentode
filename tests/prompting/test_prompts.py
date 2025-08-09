from importlib import import_module


def test_prompt_bundle_structure_and_constraints():
    # Import (will fail until implemented)
    gen = import_module("src.prompting.generator")

    task_text = "Build a doc pipeline and providers."
    # Minimal summaries with filename citations requirement
    summaries = [
        {"filename": "doc1.txt", "excerpt": "pipeline overview"},
        {"filename": "doc2.txt", "excerpt": "provider interface"},
    ]

    bundle = gen.build_prompts(task_text, summaries)

    # Must include three prompts
    assert isinstance(bundle, dict)
    assert "plan" in bundle
    assert "tickets" in bundle
    assert "checklist" in bundle

    # Each prompt must be non-empty strings and contain constraints
    for key in ["plan", "tickets", "checklist"]:
        val = bundle.get(key)
        assert isinstance(val, str)
        assert len(val) > 0
        # Should mention citations guidance
        assert "cite source filenames" in val.lower()
        # Should include headings instruction
        assert "markdown" in val.lower()

    # Plan prompt should reference architecture and testing
    assert "architecture" in bundle["plan"].lower()
    assert "testing" in bundle["plan"].lower()

    # Tickets prompt should reference IDs and acceptance criteria
    assert "ticket ids" in bundle["tickets"].lower()
    assert "acceptance criteria" in bundle["tickets"].lower()

    # Checklist prompt should reference task id format and tdd
    assert "task id format" in bundle["checklist"].lower()
    assert "tdd" in bundle["checklist"].lower()
