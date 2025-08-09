# Paths & Manifests

This document describes directory layout and manifest files produced/used by the system.

## Required Directories

- processed_documents/
  - text/
- COMBINED_RESULTS/
- logs/

Use `ensure_required_dirs(base_dir)` from `src/paths/manager.py` to create these directories idempotently.

## Attempt Directories

Per provider/developer/model and attempt:

- `{Provider}_{Developer}_{Model}/attempt_N/`
  - Example: `Anthropic_Mark_claude-3-sonnet/attempt_2/`
  - Built by `build_attempt_dir(base, provider, developer, model, attempt_num)`.
  - Unsafe characters in segments are replaced with `_` via `sanitize_folder_name()`.

## Helper Functions

All functions in `src/paths/manager.py` (functional style):
- `ensure_required_dirs(base_dir) -> dict`
- `build_attempt_dir(base_dir, provider, developer, model, attempt_num) -> str`
- `sanitize_folder_name(name) -> str`
- `join_paths(base, s1, s2, s3, s4) -> str`

## Manifests

`src/paths/manifests.py` provides JSON helpers with atomic writes:
- `save_attempt_manifest(path, data)` / `load_attempt_manifest(path)`
- `save_run_manifest(path, data)` / `load_run_manifest(path)`

### attempt_manifest.json (example keys)

```json
{
  "provider": "Anthropic",
  "developer": "Mark",
  "model": "claude-3-sonnet",
  "attempt": 2,
  "started_at": "1723170000",
  "finished_at": "1723170123",
  "parameters": { "temperature": 0, "max_tokens": 1024, "top_p": 1 }
}
```

### run_manifest.json (example keys)

```json
{
  "run_id": "abc123",
  "started_at": "1723170000",
  "providers": [
    {"provider": "Anthropic", "developer": "Anthropic", "model": "claude-3-sonnet"},
    {"provider": "OpenRouter", "developer": "OpenAI", "model": "gpt-4o"}
  ],
  "weights": {"task_relevance": 1.0, "documentation_relevance": 1.0}
}
```

Notes:
- Atomic writes prevent partial files and ensure deterministic content (sorted JSON keys).
- Avoid logging secrets. Manifests should not contain API keys.
