from dataclasses import dataclass
from typing import Any, Dict, List, TypedDict


class PromptBundle(TypedDict):
    """Structured output containing all generated prompts."""
    plan: str
    tickets: str
    checklist: str


def _truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to max_length, adding ellipsis if truncated.
    
    Args:
        text: The text to truncate
        max_length: Maximum length of the output string
    
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def _summaries_block(summaries: List[Dict[str, Any]]) -> str:
    """Format document summaries into a readable block.
    
    Args:
        summaries: List of dicts with 'filename' and 'excerpt' keys
        
    Returns:
        Formatted string with all summaries
    """
    lines: List[str] = []
    
    if not summaries:
        return "No document summaries available.\n"
        
    lines.append("## Relevant Document Summaries")
    i = 0
    while i < len(summaries):
        item = summaries[i]
        name = item.get("filename", "")
        excerpt = item.get("excerpt", "")
        
        truncated_excerpt = _truncate_text(excerpt, 300)
        lines.append(f"### {name}")
        lines.append(f"```\n{truncated_excerpt}\n```")
        lines.append("")
        i = i + 1
        
    return "\n".join(lines) + "\n"


def _get_common_constraints() -> str:
    """Return common constraints for all prompt types."""
    return """## Constraints
- Use clear Markdown formatting with appropriate headings
- Be specific and actionable in responses
- Keep responses focused and concise
- Reference source documents when applicable using [source: filename]
- Maintain consistent formatting throughout
- Use bullet points for lists and checklists
- Include all necessary context from the provided information
- Follow standard technical writing best practices
"""

def _get_plan_specific_constraints() -> str:
    """Return constraints specific to the planning prompt."""
    return """## Planning Requirements
- Start with a high-level overview
- Break down into clear phases or components
- Include technical considerations and dependencies
- Address potential risks and mitigation strategies
- Suggest implementation priorities
- Consider scalability and maintainability
- Include testing approach
- Estimate complexity/difficulty levels
"""

def _get_tickets_specific_constraints() -> str:
    """Return constraints specific to the tickets prompt."""
    return """## Ticket Requirements
- Use format: `TICKET-XXX: Short descriptive title`
- Include clear acceptance criteria
- Add implementation notes if needed
- Reference related documents or components
- Include validation criteria
- Add any relevant technical constraints
- Specify dependencies between tickets
"""

def _get_checklist_specific_constraints() -> str:
    """Return constraints specific to the checklist prompt."""
    return """## Checklist Requirements
- Use format: `- [ ] TICKET-XXX.YY: Task description`
- Break down into small, testable tasks
- Include verification steps
- Add any necessary setup/teardown steps
- Include testing tasks
- Consider edge cases and error conditions
- Add documentation tasks
"""

def _build_prompt(task: str, summaries: str, constraints: str, specific_constraints: str) -> str:
    """Construct a prompt with consistent structure.
    
    Args:
        task: The main task description
        summaries: Formatted document summaries
        constraints: Common constraints
        specific_constraints: Prompt-specific constraints
        
    Returns:
        Formatted prompt string
    """
    return f"""# Task
{task}

{summaries}

{constraints}

{specific_constraints}
"""

def build_prompts(task_text: str, summaries: List[Dict[str, Any]]) -> PromptBundle:
    """Generate structured prompts for planning, tickets, and checklists.
    
    Args:
        task_text: Description of the task to be performed
        summaries: List of document summaries with filenames and excerpts
        
    Returns:
        Dictionary containing three prompts: 'plan', 'tickets', and 'checklist'
    """
    summaries_text = _summaries_block(summaries)
    common_constraints = _get_common_constraints()
    
    plan_prompt = _build_prompt(
        task=task_text,
        summaries=summaries_text,
        constraints=common_constraints,
        specific_constraints=_get_plan_specific_constraints()
    )
    
    tickets_prompt = _build_prompt(
        task=task_text,
        summaries=summaries_text,
        constraints=common_constraints,
        specific_constraints=_get_tickets_specific_constraints()
    )
    
    checklist_prompt = _build_prompt(
        task=task_text,
        summaries=summaries_text,
        constraints=common_constraints,
        specific_constraints=_get_checklist_specific_constraints()
    )
    
    return {
        "plan": plan_prompt,
        "tickets": tickets_prompt,
        "checklist": checklist_prompt,
    }
