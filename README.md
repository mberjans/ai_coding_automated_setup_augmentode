# Automated LLM-Based Project Planning & Documentation Generation System

A functional Python project for automated project planning, ticket generation, and attempt orchestration.

## Quickstart

Follow these steps in a fresh shell.

1. Create a local virtual environment in `.venv/`:
   ```bash
   scripts/venv_create.sh
   ```
2. Activate the local virtual environment for the current shell:
   ```bash
   source scripts/venv_activate.sh
   ```
3. Verify the CLI entry works and view available commands:
   ```bash
   python -m src.cli --help
   ```

## Development

- Run tests:
  ```bash
  venv/bin/pytest -q
  ```

- Venv marker file is written to `.venv/.project_venv` to help ensure environment isolation.

## Project Structure

- `src/` — runtime code (CLI and modules)
- `tests/` — test suite (pytest)
- `scripts/` — helper scripts for venv creation/activation
- `docs/` — documentation (e.g., checklist)
- `logs/` — runtime logs

## Requirements

- Python 3.11+

This project intentionally avoids object-oriented patterns and list comprehensions, and does not use regular expressions. Prefer functional style and explicit pattern-matching functions.
