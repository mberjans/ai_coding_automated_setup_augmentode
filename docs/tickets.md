## Tickets — Automated LLM-Based Project Planning & Documentation Generation System

The following tickets are organized by implementation phases (Phase 0 → Phase 6) per docs/plan.md. Each ticket has: ID, Title, Description, Acceptance Criteria, Dependencies, Estimated Effort, Implementation Notes.

---

### Phase 0 — Project Skeleton, Config, Logging, Paths

#### TICKET-001 — Repository Skeleton & Venv Bootstrap
- Description: Create the initial Python project skeleton with a CLI entrypoint, enforce local venv usage, and establish the base folder structure and Makefile-like helper scripts.
- Acceptance criteria:
  - A Python venv is created and documented (no global packages).
  - Basic package layout present (src/ with __init__.py and cli.py), pyproject.toml or setup.cfg, .gitignore, .env.example.
  - Base folders exist: processed_documents/, COMBINED_RESULTS/ (empty), logs/.
  - Running `python -m src.cli --help` works.
- Dependencies: None
- Estimated effort: 4-6 hours
- Implementation notes:
  - Use Python 3.11+; prefer pyproject.toml for tooling.
  - Add simple shell scripts for `venv/create`, `venv/activate`.

#### TICKET-002 — Configuration Schema & Loader
- Description: Implement config.yaml schema, load/validate via pydantic, and map environment variables for secrets. Provide sensible defaults and validation errors.
- Acceptance criteria:
  - config module loads config.yaml or path passed via CLI.
  - Validation for providers, attempts, weights, rate limits, output base_dir.
  - Secrets resolved from env variables; no secrets in logs.
- Dependencies: TICKET-001
- Estimated effort: 1-2 days
- Implementation notes:
  - Add pydantic models (AppConfig, ProviderConfig, GenerationConfig, EvaluationConfig, RateLimits, LoggingConfig).
  - Provide example config in examples/config.example.yaml.

#### TICKET-003 — Structured Logging & Telemetry Scaffolding
- Description: Implement JSON logging with levels, redaction of secrets, and rotating file handlers; prepare hooks for optional OpenTelemetry.
- Acceptance criteria:
  - Logs written to logs/app.log in JSON format with correlation/run IDs.
  - Console logs respect log level from config.
  - Secret values are never printed.
- Dependencies: TICKET-001, TICKET-002
- Estimated effort: 4-6 hours
- Implementation notes:
  - Use standard logging with structured formatter; later add OTLP exporters behind a flag.

#### TICKET-004 — Path/Directory Manager & Manifests
- Description: Centralize all paths and constants; create helpers to materialize required directories and write run/attempt manifests.
- Acceptance criteria:
  - Utility ensures presence of processed_documents/text and COMBINED_RESULTS/.
  - Helper to format `{Provider}_{Developer}_{Model}/attempt_N/` paths.
  - Can write/read attempt_manifest.json and run manifest safely.
- Dependencies: TICKET-001
- Estimated effort: 4-6 hours
- Implementation notes:
  - Implement small path utilities; avoid regex; write explicit path join helpers.

---

### Phase 1 — Document Processing Pipeline

#### TICKET-005 — Format Detection & Routing
- Description: Detect file types by extension and safe content checks; route to the correct parser/OCR module.
- Acceptance criteria:
  - Supported formats mapped: txt, md, docx, xlsx, csv, tsv, pdf, pptx, png, jpeg, svg.
  - Unknown types logged as skipped with reason.
  - Unit tests cover mapping and routing.
- Dependencies: TICKET-004
- Estimated effort: 4-6 hours
- Implementation notes:
  - Create a registry dict of handlers; explicit if/elif logic, no regex.

#### TICKET-006 — Plain Text & Markdown Parser
- Description: Implement parsers for .txt and .md files with normalization (UTF-8, whitespace trimming, headings preserved).
- Acceptance criteria:
  - Writes processed .txt to processed_documents/text/ with safe filenames.
  - Maintains mapping entry with original path and processed path.
- Dependencies: TICKET-005
- Estimated effort: 2-4 hours
- Implementation notes:
  - Add simple front-matter stripping for .md when present (explicit scanning functions).

#### TICKET-007 — Office Docs Parser (DOCX, PPTX)
- Description: Extract text from .docx and .pptx using python-docx and python-pptx, preserving slide/section boundaries in plain text.
- Acceptance criteria:
  - DOCX paragraphs concatenated; PPTX slides separated with clear markers.
  - Mapping entries include parser name and counts (paragraphs/slides).
- Dependencies: TICKET-005
- Estimated effort: 1-2 days
- Implementation notes:
  - Normalize newlines; drop control characters.

#### TICKET-008 — Spreadsheet & Tabular Parser (XLSX, CSV, TSV)
- Description: Extract cell text from spreadsheets and tabular files; represent each sheet as a simple TSV-like text with headers.
- Acceptance criteria:
  - XLSX sheets exported; CSV/TSV normalized to tab-separated text output.
  - Mapping captures sheet names and row counts.
- Dependencies: TICKET-005
- Estimated effort: 1-2 days
- Implementation notes:
  - Use openpyxl for xlsx; use csv module for csv/tsv.

#### TICKET-009 — PDF Text Extraction with OCR Fallback
- Description: Extract text from PDFs using pdfminer/pypdf; if low text yield, fall back to pytesseract OCR per page.
- Acceptance criteria:
  - Text extracted for searchable PDFs; OCR used for scanned PDFs when needed.
  - Mapping indicates pages processed and ocr_used flag.
- Dependencies: TICKET-005
- Estimated effort: 1-2 days
- Implementation notes:
  - Implement text-coverage heuristic (character count threshold) to trigger OCR.

#### TICKET-010 — Image OCR (PNG/JPEG) and SVG Extraction
- Description: OCR image formats with pytesseract; extract textual nodes from SVG using XML parsing.
- Acceptance criteria:
  - Images converted to text with language from config.
  - SVG text elements concatenated in reading order.
- Dependencies: TICKET-005
- Estimated effort: 4-6 hours
- Implementation notes:
  - Provide configuration for OCR engine and language.

#### TICKET-011 — Normalization Pipeline
- Description: Normalize all processed text (UTF-8, newline policy, whitespace, simple header/footer stripping) and sanitize filenames.
- Acceptance criteria:
  - Consistent newline and whitespace policy across all outputs.
  - Unit tests verify normalization behavior.
- Dependencies: TICKET-006, TICKET-007, TICKET-008, TICKET-009, TICKET-010
- Estimated effort: 4-6 hours
- Implementation notes:
  - Implement explicit scanning functions for header/footer removal; avoid regex.

#### TICKET-012 — Mapping Writer & Pipeline Error Handling
- Description: Write processed_documents/mapping.json with rich metadata; implement error taxonomy and per-file error capture without halting the pipeline.
- Acceptance criteria:
  - mapping.json contains: original_path, processed_relpath, format, parser, pages/sheets (if any), ocr_used, timestamps, checksum, error (if any).
  - Pipeline continues on individual file failures; errors logged.
- Dependencies: TICKET-011
- Estimated effort: 4-6 hours
- Implementation notes:
  - Use checksums to detect unchanged files and enable incremental runs later.

---

### Phase 2 — Provider Abstraction, Prompts, Attempt Runner, Adapters

#### TICKET-013 — Provider Interface & Registry
- Description: Define ProviderClient interface (prepare_prompt, call) and registry; standardize request/response structures and error types.
- Acceptance criteria:
  - Interface methods defined with type hints and docstrings.
  - Registry can resolve providers by name from config.
- Dependencies: TICKET-004, TICKET-002, TICKET-003
- Estimated effort: 4-6 hours
- Implementation notes:
  - Keep interface minimal and explicit; no dynamic magic.

#### TICKET-014 — Prompt Generator for plan.md, tickets.md, checklist.md
- Description: Implement deterministic prompt templates that ground on task description and processed doc summaries with filename citations.
- Acceptance criteria:
  - Prompt builder returns three structured prompts with clear output constraints.
  - Unit tests verify presence of required sections and citations guidance.
- Dependencies: TICKET-013, TICKET-012
- Estimated effort: 4-6 hours
- Implementation notes:
  - Provide small summarizer over processed text to include short excerpts.

#### TICKET-015 — Attempt Runner & Directory Management
- Description: Implement per-provider attempt execution, directory creation, artifact writing, and attempt_manifest.json persistence.
- Acceptance criteria:
  - Creates {Provider}_{Developer}_{Model}/attempt_N/ directories.
  - Saves prompts, responses, plan.md, tickets.md, checklist.md, and attempt_manifest.json.
- Dependencies: TICKET-013, TICKET-014, TICKET-004
- Estimated effort: 1-2 days
- Implementation notes:
  - Store all request parameters, seeds, and token counts in manifest.

#### TICKET-016 — Anthropic Provider Adapter
- Description: Implement adapter using Anthropic API per config (model, temperature, top_p, seed when supported).
- Acceptance criteria:
  - Successful calls with retry/backoff on 429/5xx.
  - Errors surfaced with ProviderError and recorded in attempt_manifest.json.
- Dependencies: TICKET-013, TICKET-015
- Estimated effort: 1-2 days
- Implementation notes:
  - Use httpx async client; honor rate limits from config (to be wired in Phase 5).

#### TICKET-017 — OpenRouter (OpenAI-Compatible) Adapter
- Description: Implement adapter for OpenRouter routing to OpenAI-compatible chat/completions.
- Acceptance criteria:
  - Successful calls using configured model; parameters persisted.
  - Works within Attempt Runner and produces artifacts.
- Dependencies: TICKET-013, TICKET-015
- Estimated effort: 1-2 days
- Implementation notes:
  - Support per-request headers for OpenRouter; ensure key isolation.

---

### Phase 3 — Judge/Evaluation & Ranking

#### TICKET-018 — LLM-as-Judge Engine & Rubric
- Description: Implement evaluation engine that scores Task Relevance and Documentation Relevance (0.0–1.0) with rationale, using a configured judge model.
- Acceptance criteria:
  - Produces evaluation.json per attempt with two scores and rationale.
  - Supports configurable weights (default equal).
- Dependencies: TICKET-015
- Estimated effort: 4-6 hours
- Implementation notes:
  - Reuse ProviderClient where possible for judge calls or a dedicated lightweight adapter.

#### TICKET-019 — Ranking & Metadata Outputs
- Description: Compute weighted averages, rank all attempts, select the best baseline, and write COMBINED_RESULTS/metadata.json.
- Acceptance criteria:
  - Ranking includes scores, weights, tie-breakers, selected baseline path.
  - metadata.json saved in COMBINED_RESULTS/ with run details.
- Dependencies: TICKET-018, TICKET-004
- Estimated effort: 4-6 hours
- Implementation notes:
  - Implement deterministic tie-breakers: lower temperature, earliest timestamp.

---

### Phase 4 — Combination Engine

#### TICKET-020 — Combination Strategy Engine
- Description: Based on the top-ranked attempt, analyze other attempts to suggest beneficial sections; generate enhanced plan.md, tickets.md, and checklist.md.
- Acceptance criteria:
  - Produces combined docs under COMBINED_RESULTS/.
  - Captures combination rationale and citations to source attempts in metadata.
- Dependencies: TICKET-019
- Estimated effort: 1-2 days
- Implementation notes:
  - Use an LLM prompt to extract improvements; limit scope to relevant diffs.

#### TICKET-021 — ID Normalization & Conflict Resolution
- Description: Ensure ticket IDs and checklist IDs remain consistent; resolve collisions by mapping to new deterministic suffixes.
- Acceptance criteria:
  - No duplicate IDs in combined outputs; mapping recorded in metadata.
  - Validation step fails the combine if collisions are unresolved.
- Dependencies: TICKET-020
- Estimated effort: 4-6 hours
- Implementation notes:
  - Implement explicit ID map builder; avoid regex; use parsing helpers.

---

### Phase 5 — CLI, Progress, Rate Limiting, Error Recovery, Reproducibility

#### TICKET-022 — CLI Commands & UX
- Description: Implement CLI with subcommands: run, process-docs, generate, evaluate, combine; add progress bars and summary report.
- Acceptance criteria:
  - `--help` shows all commands and flags.
  - Commands execute respective pipeline stages with clear progress output.
- Dependencies: TICKET-002, TICKET-004, TICKET-015, TICKET-019, TICKET-021
- Estimated effort: 1-2 days
- Implementation notes:
  - Use rich for progress; keep commands small and explicit.

#### TICKET-023 — Rate Limiting & Retries
- Description: Implement per-provider token/rate limiters and robust retry/backoff with jitter; add circuit breaker for repeated failures.
- Acceptance criteria:
  - 429/5xx handled with exponential backoff; limiter prevents bursts beyond config.
  - Telemetry records retry counts and breaker trips.
- Dependencies: TICKET-016, TICKET-017
- Estimated effort: 1-2 days
- Implementation notes:
  - Use tenacity/backoff; implement simple token bucket per provider.

#### TICKET-024 — Error Taxonomy & Propagation
- Description: Define and use explicit error classes (ParsingError, ProviderError, RateLimitError, JudgeError, CombineError) and ensure user-facing messages are actionable.
- Acceptance criteria:
  - Errors consistently raised/caught; logs include context, file/attempt IDs.
  - CLI exits with non-zero codes on fatal errors; partial artifacts preserved.
- Dependencies: TICKET-003, TICKET-012, TICKET-015
- Estimated effort: 4-6 hours
- Implementation notes:
  - Central error module; map exceptions to codes.

#### TICKET-025 — Reproducibility & Manifests
- Description: Persist seeds, parameters, prompts, checksums; ensure runs are reproducible where provider supports it.
- Acceptance criteria:
  - attempt_manifest.json includes all parameters and seeds.
  - A dry-run mode prints planned actions without calling providers.
- Dependencies: TICKET-015, TICKET-022
- Estimated effort: 4-6 hours
- Implementation notes:
  - Add run ID; verify manifest completeness via unit tests.

---

### Phase 6 — Testing, CI/CD, Containerization, Docs, Observability

#### TICKET-026 — Parser Unit Tests & Fixtures
- Description: Add comprehensive unit tests for all parsers, normalization, routing, and mapping.json writer using small fixture documents.
- Acceptance criteria:
  - pytest suite with coverage for all supported formats and normalization.
  - Tests pass in isolated venv.
- Dependencies: TICKET-006, TICKET-007, TICKET-008, TICKET-009, TICKET-010, TICKET-011, TICKET-012
- Estimated effort: 1-2 days
- Implementation notes:
  - Use pytest and respx/mocks where needed.

#### TICKET-027 — Mocked Provider & Attempt Runner Tests
- Description: Add integration tests for Attempt Runner and Provider adapters using mocked HTTP and golden files.
- Acceptance criteria:
  - Deterministic tests verify artifacts written and manifests populated.
  - Error scenarios (429/5xx) are covered.
- Dependencies: TICKET-015, TICKET-016, TICKET-017, TICKET-023, TICKET-025
- Estimated effort: 1-2 days
- Implementation notes:
  - Use respx for httpx; generate small golden outputs.

#### TICKET-028 — Judge, Ranking, and Combination Tests
- Description: Add tests covering judge scoring, ranking/tie-breakers, and combination logic including ID conflict handling.
- Acceptance criteria:
  - Ranking stable with given weights and inputs.
  - Combined outputs validated (no duplicate IDs) and metadata rationale present.
- Dependencies: TICKET-018, TICKET-019, TICKET-020, TICKET-021
- Estimated effort: 1-2 days
- Implementation notes:
  - Use small synthetic attempts to simulate merges.

#### TICKET-029 — CI Setup (Lint/Type/Coverage)
- Description: Configure CI to run linting, type checks, and tests on push/PR; enforce minimum coverage.
- Acceptance criteria:
  - CI workflow file present; all checks pass on main branch.
  - Coverage threshold enforced (e.g., 80%).
- Dependencies: TICKET-026, TICKET-027, TICKET-028
- Estimated effort: 4-6 hours
- Implementation notes:
  - Use ruff/flake8, mypy, pytest-cov.

#### TICKET-030 — Containerization (Dockerfile) & Local Run Docs
- Description: Provide a minimal Dockerfile with optional Tesseract layer; document volume mounts and environment variables.
- Acceptance criteria:
  - Image builds locally; `run` command works with mounted source docs.
  - README updated with Docker usage instructions.
- Dependencies: TICKET-005 → TICKET-025
- Estimated effort: 4-6 hours
- Implementation notes:
  - Multi-stage build; keep image small; allow toggling OCR engine.

#### TICKET-031 — User Documentation & Examples
- Description: Write README and docs for configuration, CLI usage, provider setup, and troubleshooting; include example configs and sample run.
- Acceptance criteria:
  - README documents full workflow end-to-end.
  - Examples directory contains sample config and tiny input set.
- Dependencies: TICKET-022, TICKET-025, TICKET-029, TICKET-030
- Estimated effort: 1-2 days
- Implementation notes:
  - Include a quickstart and a troubleshooting matrix.

