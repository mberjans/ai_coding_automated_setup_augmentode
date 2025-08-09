from typing import Any, Dict, List


def _summaries_block(summaries: List[Dict[str, Any]]) -> str:
    lines: List[str] = []
    lines.append("Processed document summaries (filename: excerpt):")
    i = 0
    while i < len(summaries):
        item = summaries[i]
        name = item.get("filename", "")
        excerpt = item.get("excerpt", "")
        lines.append(f"- {name}: {excerpt}")
        i = i + 1
    return "\n".join(lines)


def _constraints_block() -> str:
    # Must include mentions used by tests: cite source filenames, markdown
    parts: List[str] = []
    parts.append("Constraints:")
    parts.append("- Use Markdown headings and clear structure.")
    parts.append("- Cite source filenames when using information (e.g., [source: filename.txt]).")
    parts.append("- Keep outputs deterministic and concise.")
    return "\n".join(parts)


def build_prompts(task_text: str, summaries: List[Dict[str, Any]]) -> Dict[str, str]:
    # shared
    summaries_text = _summaries_block(summaries)
    constraints = _constraints_block()

    # plan prompt
    plan_lines: List[str] = []
    plan_lines.append("# PLAN REQUEST (Markdown)")
    plan_lines.append("Task:")
    plan_lines.append(task_text)
    plan_lines.append("")
    plan_lines.append(summaries_text)
    plan_lines.append("")
    plan_lines.append(constraints)
    plan_lines.append("- Include sections on Architecture, Components, Testing, Risks.")
    plan_prompt = "\n".join(plan_lines)

    # tickets prompt
    tickets_lines: List[str] = []
    tickets_lines.append("# TICKETS REQUEST (Markdown)")
    tickets_lines.append("Task:")
    tickets_lines.append(task_text)
    tickets_lines.append("")
    tickets_lines.append(summaries_text)
    tickets_lines.append("")
    tickets_lines.append(constraints)
    tickets_lines.append("- Provide Ticket IDs and Acceptance Criteria per ticket.")
    tickets_prompt = "\n".join(tickets_lines)

    # checklist prompt
    checklist_lines: List[str] = []
    checklist_lines.append("# CHECKLIST REQUEST (Markdown)")
    checklist_lines.append("Task:")
    checklist_lines.append(task_text)
    checklist_lines.append("")
    checklist_lines.append(summaries_text)
    checklist_lines.append("")
    checklist_lines.append(constraints)
    checklist_lines.append("- Use task ID format {ticket_id}.{task_id} and emphasize TDD.")
    checklist_prompt = "\n".join(checklist_lines)

    return {
        "plan": plan_prompt,
        "tickets": tickets_prompt,
        "checklist": checklist_prompt,
    }
