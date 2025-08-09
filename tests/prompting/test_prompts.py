from importlib import import_module
import pytest


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
        assert "reference source documents" in val.lower() or "[source: filename]" in val.lower()
        # Should include markdown formatting instructions
        assert "markdown" in val.lower()

    # Plan prompt should reference architecture and testing
    plan_lower = bundle["plan"].lower()
    assert any(term in plan_lower for term in ["architecture", "technical considerations", "scalability"])
    assert "testing" in plan_lower or "test approach" in plan_lower

    # Tickets prompt should reference IDs and acceptance criteria
    tickets_lower = bundle["tickets"].lower()
    assert any(term in tickets_lower for term in ["ticket-", "acceptance criteria"])
    assert "implementation" in tickets_lower or "requirements" in tickets_lower

    # Checklist prompt should reference task id format and tdd
    checklist_lower = bundle["checklist"].lower()
    assert any(term in checklist_lower for term in ["ticket-", "task description"])
    assert any(term in checklist_lower for term in ["test", "verification", "tdd"])


def test_summary_inclusion_and_citations():
    """Verify summaries are included with proper citations and length limits."""
    gen = import_module("src.prompting.generator")
    
    # Test with realistic document summaries
    test_summaries = [
        {"filename": "requirements.txt", "excerpt": "pytest>=7.0.0\nrequests>=2.28.0"},
        {"filename": "README.md", "excerpt": "# Project\n\nA document processing pipeline with LLM integration."},
        {"filename": "src/main.py", "excerpt": "def main():\n    print(\"Hello world\")"}
    ]
    
    bundle = gen.build_prompts("Test task", test_summaries)
    
    # Check each summary is included with its filename
    for item in test_summaries:
        filename = item["filename"]
        excerpt = item["excerpt"]
        
        # Filename should appear in each prompt
        for prompt in bundle.values():
            assert filename in prompt, f"Filename {filename} not found in prompt"
            
            # Excerpt content should appear (may be truncated)
            max_excerpt = 100  # Reasonable length for excerpt inclusion
            truncated = excerpt[:max_excerpt]
            if len(excerpt) > max_excerpt:
                truncated = excerpt[:max_excerpt-3] + "..."
            assert truncated in prompt, f"Excerpt for {filename} not found in prompt"
    
    # Test with empty summaries
    empty_bundle = gen.build_prompts("Empty test", [])
    for prompt in empty_bundle.values():
        assert "no document summaries available" in prompt.lower()


def test_summary_length_limits():
    """Verify long summaries are properly truncated."""
    gen = import_module("src.prompting.generator")
    
    # Create a very long excerpt
    long_text = "A" * 1000  # 1000 character excerpt
    summaries = [{"filename": "long.txt", "excerpt": long_text}]
    
    bundle = gen.build_prompts("Length test", summaries)
    
    # The full excerpt should not appear in any prompt
    for prompt in bundle.values():
        assert len(prompt) < 2000  # Reasonable max length for a prompt section
        assert long_text not in prompt
        # But a truncated version should be there
        assert "A" * 50 in prompt  # First part should be included
        assert "..." in prompt  # Indicates truncation
