"""Judge scoring functions for task and documentation relevance."""


def score_task_relevance(prompt: str, response: str):
    """Score the relevance of a response to a task prompt.
    
    Args:
        prompt: The original task prompt
        response: The response to score
        
    Returns:
        Dictionary with 'score' and 'rationale' keys
    """
    if not response:
        return {"score": 0.0, "rationale": "Empty response"}
    
    # Simple keyword-based scoring
    prompt_words = set(prompt.lower().split())
    response_words = set(response.lower().split())
    
    # Count overlapping words
    overlap = len(prompt_words.intersection(response_words))
    total = len(prompt_words.union(response_words))
    
    if total == 0:
        return {"score": 0.0, "rationale": "No overlapping keywords"}
    
    score = min(1.0, overlap / total)
    rationale = f"Found {overlap} overlapping keywords out of {total} total unique words"
    
    return {"score": score, "rationale": rationale}


def score_documentation_relevance(prompt: str, response: str):
    """Score the relevance of a response to a documentation prompt.
    
    Args:
        prompt: The original documentation prompt
        response: The response to score
        
    Returns:
        Dictionary with 'score' and 'rationale' keys
    """
    if not response:
        return {"score": 0.0, "rationale": "Empty response"}
    
    # Simple keyword-based scoring
    prompt_words = set(prompt.lower().split())
    response_words = set(response.lower().split())
    
    # Count overlapping words
    overlap = len(prompt_words.intersection(response_words))
    total = len(prompt_words.union(response_words))
    
    if total == 0:
        return {"score": 0.0, "rationale": "No overlapping keywords"}
    
    score = min(1.0, overlap / total)
    rationale = f"Found {overlap} overlapping keywords out of {total} total unique words"
    
    return {"score": score, "rationale": rationale}
