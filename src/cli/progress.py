"""CLI progress display utilities using rich Console.

Functional style. No OOP, no list comprehensions, no regex.
"""
import time
from typing import Any, Dict, List, Optional

from rich.console import Console


def display_progress(stages: List[str], console: Optional[Console] = None, step_delay: float = 0.1) -> Dict[str, Any]:
    if console is None:
        console = Console()

    durations: Dict[str, float] = {}
    i = 0
    console.print("Starting pipeline...")
    while i < len(stages):
        stage = stages[i]
        start = time.time()
        console.print(f"[bold cyan]Stage:[/bold cyan] {stage}")
        if step_delay and step_delay > 0:
            time.sleep(step_delay)
        end = time.time()
        durations[stage] = float(end - start)
        console.print(f"Completed: {stage}")
        i = i + 1
    console.print("Completed pipeline")
    return {"total_stages": len(stages), "durations": durations}
