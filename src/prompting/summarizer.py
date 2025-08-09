from typing import List, Dict, Any, Optional
import os
from pathlib import Path


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
        
    # Split into sentences (simple approach - split on periods followed by space or newline)
    sentences = []
    current = []
    i = 0
    text_length = len(text)
    
    while i < text_length:
        char = text[i]
        current.append(char)
        
        # Check for sentence end
        if char in {'.', '!', '?'}:
            # Look ahead for end of sentence
            j = i + 1
            while j < text_length and text[j].isspace():
                current.append(text[j])
                j += 1
                
            # If we've reached the end or found a capital letter, it's likely a sentence end
            if j >= text_length or (j < text_length and text[j].isupper()):
                sentence = ''.join(current).strip()
                if sentence:
                    sentences.append(sentence)
                current = []
                
        i += 1
    
    # Add any remaining text
    if current:
        sentence = ''.join(current).strip()
        if sentence:
            sentences.append(sentence)
    
    # Return first few sentences as summary
    return sentences[:num_sentences]


def summarize_text(text: str, max_length: int = 200) -> str:
    """Summarize text to a specified length.
    
    Args:
        text: Text to summarize
        max_length: Maximum length of summary (including ellipsis if added)
        
    Returns:
        Summarized text
    """
    if not text.strip():
        return "[Empty]"
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # If text is already short enough, return as is
    if len(text) <= max_length:
        return text
    
    # Reserve space for ellipsis if needed
    effective_max = max_length - 3  # Account for '...'
    if effective_max < 1:
        return "..."
    
    # Find the last space before effective_max to avoid cutting words
    truncated = text[:effective_max]
    last_space = truncated.rfind(' ')
    
    # If we found a space, use it; otherwise, just truncate at max_length
    if last_space > 0:
        truncated = truncated[:last_space]
    
    # Add ellipsis
    truncated = truncated.rstrip(' .,!?') + '...'
    
    # Final check to ensure we didn't exceed max_length
    if len(truncated) > max_length:
        truncated = truncated[:max_length-3] + '...'
    
    return truncated


def read_file_content(filepath: str) -> str:
    """Read file content with error handling.
    
    Args:
        filepath: Path to the file
        
    Returns:
        File content as string
    """
    try:
        path = Path(filepath)
        if not path.is_file():
            return f"[File not found: {filepath}]"
            
        content = path.read_text(encoding='utf-8', errors='replace').strip()
        return content if content else "[Empty file]"
        
    except Exception as e:
        return f"[Error reading {filepath}: {str(e)}]"


def create_document_summaries(filepaths: List[str]) -> List[Dict[str, str]]:
    """Create summaries for multiple document files.
    
    Args:
        filepaths: List of file paths to process
        
    Returns:
        List of dictionaries with 'filename' and 'excerpt' keys
    """
    summaries = []
    
    for filepath in filepaths:
        if not filepath:
            continue
            
        filename = os.path.basename(filepath)
        content = read_file_content(filepath)
        
        # For markdown files, try to preserve structure
        if filename.lower().endswith(('.md', '.markdown')):
            # Take first few lines that aren't just whitespace
            lines = [line for line in content.split('\n') if line.strip()]
            excerpt = '\n'.join(lines[:5])  # First 5 non-empty lines
        else:
            # For other files, take first meaningful sentences
            excerpt = ' '.join(extract_key_sentences(content, 2))
            
            # If we didn't get good sentences, fall back to first part of content
            if not excerpt.strip():
                excerpt = content[:200].strip()
                if len(content) > 200:
                    excerpt += '...'
        
        summaries.append({
            'filename': filename,
            'excerpt': excerpt
        })
    
    return summaries
