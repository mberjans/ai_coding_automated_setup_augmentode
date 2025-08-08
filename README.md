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

## Configuration

Configuration is provided via a YAML file. An example is available at `examples/config.example.yaml`.

- **providers.anthropic.api_key_env**: Name of the environment variable containing your API key. The loader validates that this env var exists but does not log its name or value.
- **providers.anthropic.models**: Optional list of model identifiers to use.
- **generation.temperature**: Float in [0.0, 2.0].
- **generation.max_tokens**: Positive integer.
- **generation.attempts**: Non-negative integer.
- **evaluation.weights.task_relevance**: Float in [0.0, 1.0].
- **evaluation.weights.documentation_relevance**: Float in [0.0, 1.0].
- **logging.level**: One of CRITICAL, ERROR, WARNING, INFO, DEBUG.
- **logging.file_path**: Path to the log file (e.g., `logs/app.log`).
- **rate_limits.requests_per_minute**, **rate_limits.burst**: Optional rate limiting parameters.

Environment variables are merged at runtime. Secrets are never emitted to logs.

## Requirements

- Python 3.11+

This project intentionally avoids object-oriented patterns and list comprehensions, and does not use regular expressions. Prefer functional style and explicit pattern-matching functions.
