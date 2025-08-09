from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterable, Tuple
import os

# Constants
ELLIPSIS = '...'
EMPTY_PLACEHOLDER = "[Empty]"
FILE_NOT_FOUND_PREFIX = "[File not found: "
ERROR_READING_PREFIX = "[Error reading "


@dataclass
class DocumentSummary:
    """Data class to hold document summary information."""
    filename: str
    excerpt: str


def is_sentence_ender(char: str) -> bool:
    """Check if a character typically ends a sentence."""
    return char in {'.', '!', '?'}


def find_sentence_end(text: str, start_pos: int) -> int:
    """Find the end position of a sentence starting at start_pos."""
    text_length = len(text)
    if start_pos >= text_length:
        return text_length

    i = start_pos
    while i < text_length:
        if is_sentence_ender(text[i]):
            # Look ahead for end of sentence
            j = i + 1
            while j < text_length and text[j].isspace():
                j += 1
            
            # If we've reached the end or found a capital letter, it's likely a sentence end
            if j >= text_length or text[j].isupper():
                return j
        i += 1
    
    return text_length


def extract_key_sentences(text: str, num_sentences: int = 3) -> List[str]:
    """Extract key sentences from text.
    
    Args:
        text: Input text to summarize
        num_sentences: Maximum number of sentences to return
        
    Returns:
        List of key sentences
    """
    if not text.strip():
        return []
    
    sentences = []
    pos = 0
    text_length = len(text)
    
    while pos < text_length and len(sentences) < num_sentences:
        end_pos = find_sentence_end(text, pos)
        if end_pos > pos:  # Found a sentence
            sentence = text[pos:end_pos].strip()
            if sentence:
                sentences.append(sentence)
        pos = end_pos + 1
    
    return sentences


def truncate_to_word_boundary(text: str, max_length: int) -> str:
    """Truncate text to the nearest word boundary before max_length."""
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > 0:
        return truncated[:last_space].rstrip(' .,!?')
    return truncated.rstrip(' .,!?')


def summarize_text(text: str, max_length: int = 200) -> str:
    """Summarize text to a specified length.
    
    Args:
        text: Text to summarize
        max_length: Maximum length of summary (including ellipsis if added)
        
    Returns:
        Summarized text
    """
    if not text.strip():
        return EMPTY_PLACEHOLDER
    
    text = text.strip()
    if len(text) <= max_length:
        return text
    
    if max_length <= 3:  # Only room for ellipsis
        return ELLIPSIS
    
    truncated = truncate_to_word_boundary(text, max_length - len(ELLIPSIS))
    return f"{truncated}{ELLIPSIS}"


def read_file_content(filepath: str) -> str:
    """Read file content with error handling.
    
    Args:
        filepath: Path to the file
        
    Returns:
        File content as string with error handling
    """
    try:
        path = Path(filepath)
        if not path.is_file():
            return f"{FILE_NOT_FOUND_PREFIX}{filepath}]"
        
        content = path.read_text(encoding='utf-8', errors='replace').strip()
        return content if content else f"{EMPTY_PLACEHOLDER} file"
        
    except Exception as e:
        return f"{ERROR_READING_PREFIX}{filepath}: {str(e)}]"


def create_markdown_summary(content: str) -> str:
    """Create a summary for markdown content."""
    lines = [line for line in content.split('\n') if line.strip()]
    return '\n'.join(lines[:5])  # First 5 non-empty lines


def create_generic_summary(content: str) -> str:
    """Create a summary for generic text content."""
    excerpt = ' '.join(extract_key_sentences(content, 2))
    if not excerpt.strip():
        excerpt = summarize_text(content, 200)
    return excerpt


def create_document_summaries(filepaths: Iterable[str]) -> List[Dict[str, str]]:
    """Create summaries for multiple document files.
    
    Args:
        filepaths: Iterable of file paths to process
        
    Returns:
        List of dictionaries with 'filename' and 'excerpt' keys
    """
    summaries = []
    
    for filepath in filepaths:
        if not filepath:
            continue
            
        filename = os.path.basename(filepath)
        content = read_file_content(filepath)
        
        if filename.lower().endswith(('.md', '.markdown')):
            excerpt = create_markdown_summary(content)
        else:
            excerpt = create_generic_summary(content)
        
        summaries.append(DocumentSummary(filename=filename, excerpt=excerpt))
    
    # Convert to list of dicts for backward compatibility
    return [{"filename": s.filename, "excerpt": s.excerpt} for s in summaries]
