import os
import tempfile
import pytest
from pathlib import Path
from typing import List, Dict, Any


def test_create_document_summaries():
    """Test creating summaries from document files."""
    # Import inside test to ensure we get the latest version
    summarizer = __import__("src.prompting.summarizer", fromlist=["create_document_summaries"])
    
    # Create a temporary directory with test files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        test_files = {
            "doc1.txt": "This is a test document about Python programming. "
                       "It contains multiple sentences to test the summarizer. "
                       "The summarizer should extract key points from this text.",
            "notes.md": "# Project Notes\n\n- Important: Complete the summarizer\n- Deadline: 2024-01-01\n\n## Details\nThis is a markdown file with structured content.",
            "empty.txt": ""
        }
        
        # Write test files
        file_paths = []
        for filename, content in test_files.items():
            path = Path(temp_dir) / filename
            path.write_text(content)
            file_paths.append(str(path))
        
        # Test with default settings
        result = summarizer.create_document_summaries(file_paths)
        
        # Verify basic structure
        assert isinstance(result, list)
        assert len(result) == len(test_files)
        
        # Check each summary
        for summary in result:
            assert "filename" in summary
            assert "excerpt" in summary
            assert isinstance(summary["filename"], str)
            assert isinstance(summary["excerpt"], str)
            
            # Check content based on file type
            if summary["filename"] == "doc1.txt":
                # Should contain first sentence or key phrases
                assert "test document" in summary["excerpt"].lower()
            elif summary["filename"] == "notes.md":
                # Should include markdown headers and important points
                assert "project notes" in summary["excerpt"].lower()
                assert "important:" in summary["excerpt"].lower()
            elif summary["filename"] == "empty.txt":
                assert summary["excerpt"] == "[Empty file]"


def test_summarize_text():
    """Test the text summarization function."""
    summarizer = __import__("src.prompting.summarizer", fromlist=["summarize_text"])
    
    # Test with simple text
    text = """
    Python is a high-level programming language. It is widely used for web development, 
    data analysis, artificial intelligence, and more. The language was created by 
    Guido van Rossum and first released in 1991.
    """
    
    # Test different max_length values
    for length in [50, 100, 200]:
        summary = summarizer.summarize_text(text, max_length=length)
        assert isinstance(summary, str)
        assert len(summary) <= length
        
        # Should contain key terms
        assert "python" in summary.lower()
        assert "programming" in summary.lower()
    
    # Test with very short text
    assert summarizer.summarize_text("Short text") == "Short text"
    
    # Test with empty string
    assert summarizer.summarize_text("") == "[Empty]"


def test_extract_key_sentences():
    """Test extracting key sentences from text."""
    summarizer = __import__("src.prompting.summarizer", fromlist=["extract_key_sentences"])
    
    text = """
    Python is a high-level programming language. It is widely used for web development. 
    The language was created by Guido van Rossum. Python has a large standard library.
    """
    
    # Test different numbers of sentences
    for count in [1, 2, 3]:
        sentences = summarizer.extract_key_sentences(text, num_sentences=count)
        assert isinstance(sentences, list)
        assert len(sentences) == min(count, len(text.split('. ')))
        
        # Each item should be a string
        for s in sentences:
            assert isinstance(s, str)
            assert len(s) > 0
    
    # Test with empty string
    assert summarizer.extract_key_sentences("") == []
