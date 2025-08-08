## Checklists — Automated LLM-Based Project Planning & Documentation Generation System

Task ID format: {ticket_id}.{task_id}. All tasks start with tests (TDD), then implementation, then verification and cleanup.

---

### Phase 0 — Project Skeleton, Config, Logging, Paths

#### TICKET-001 — Repository Skeleton & Venv Bootstrap
- [x] TICKET-001.01 Create tests/test_cli_help.py with a failing test asserting `python -m src.cli --help` exits 0 and prints command list.
- [x] TICKET-001.02 Create tests/test_env_isolation.py asserting a venv marker file exists and global site-packages are not used.
- [x] TICKET-001.03 Implement src/cli.py minimal argparse with `--help` and subcommand placeholders (no side effects).
- [x] TICKET-001.04 Create project scaffolding: src/__init__.py, pyproject.toml (runtime + test deps), .gitignore, .env.example, logs/.
- [x] TICKET-001.05 Add scripts/venv_create.sh and scripts/venv_activate.sh to create/activate Python venv in .venv/.
- [x] TICKET-001.06 Add a venv marker file at .venv/.project_venv and a runtime check in src/__init__.py to warn if not in venv.
- [x] TICKET-001.07 Implement basic package entry `python -m src.cli` path and verify module discovery works locally.
- [x] TICKET-001.08 Run tests; ensure CLI help test passes; ensure env isolation test passes; refactor argparse setup for clarity.
- [x] TICKET-001.09 Document quickstart in README section: venv creation, activation, run `python -m src.cli --help`.

#### TICKET-002 — Configuration Schema & Loader
- [x] TICKET-002.01 Write failing tests in tests/config/test_loader.py for: default config load, custom path load, validation errors, env var secret mapping.
- [x] TICKET-002.02 Write tests for edge cases: unknown provider fields are rejected; negative attempts invalid; missing API key env raises friendly error.
- [x] TICKET-002.03 Implement src/config/models.py using pydantic for AppConfig, ProviderConfig, GenerationConfig, EvaluationConfig, RateLimits, LoggingConfig.
- [x] TICKET-002.04 Implement src/config/loader.py to load YAML from path or default, merge env vars, and validate with models; no secrets in logs.
- [x] TICKET-002.05 Provide examples/config.example.yaml; update tests to load from fixtures/configs/.
- [x] TICKET-002.06 Implement src/config/validation.py with explicit value checks (no regex) for weights, attempts, and directories.
- [x] TICKET-002.07 Run tests; confirm failures turn green; refactor config loader for readability; ensure type hints complete.
- [ ] TICKET-002.08 Add documentation block in README for configuration keys and environment variables.

#### TICKET-003 — Structured Logging & Telemetry Scaffolding
- [ ] TICKET-003.01 Write failing tests in tests/logging/test_json_logger.py asserting JSON structure, levels, and redaction of API keys.
- [ ] TICKET-003.02 Write tests that rotating file handler writes to logs/app.log and console level respects config.
- [ ] TICKET-003.03 Implement src/logging/json_logger.py with get_logger(name, level) returning structured logger; add redaction filter.
- [ ] TICKET-003.04 Implement src/logging/handlers.py configuring file and console handlers; ensure per-run correlation ID.
- [ ] TICKET-003.05 Wire logger into src/cli.py for `--verbose` flag support.
- [ ] TICKET-003.06 Run tests; verify redaction works for strings containing patterns like "key=" and environment variable names.
- [ ] TICKET-003.07 Refactor logging setup for minimal global state; document logging usage in docs/.

#### TICKET-004 — Path/Directory Manager & Manifests
- [ ] TICKET-004.01 Write failing tests in tests/paths/test_manager.py for ensuring processed_documents/text, COMBINED_RESULTS/, logs/ are created if missing.
- [ ] TICKET-004.02 Write tests for formatting provider attempt paths: {Provider}_{Developer}_{Model}/attempt_N/.
- [ ] TICKET-004.03 Write tests for attempt_manifest.json save/load roundtrip including timestamps and parameters.
- [ ] TICKET-004.04 Implement src/paths/manager.py with explicit join helpers (no regex), sanitizing folder names.
- [ ] TICKET-004.05 Implement src/paths/manifests.py to write/read attempt_manifest.json and run manifest with error-safe writes.
- [ ] TICKET-004.06 Run tests; ensure directory creation is idempotent; refactor path helpers for clarity.
- [ ] TICKET-004.07 Add developer doc snippet on directory layout and manifests.

---

### Phase 1 — Document Processing Pipeline

#### TICKET-005 — Format Detection & Routing
- [x] TICKET-005.01 Write failing tests in tests/processing/test_detection.py mapping extensions to handlers (txt, md, docx, xlsx, csv, tsv, pdf, pptx, png, jpeg, svg).
- [x] TICKET-005.02 Add tests for unknown/unsupported extensions → skipped with reason; ensure logs contain skip entry.
- [x] TICKET-005.03 Implement src/processing/detection.py with explicit if/elif routing to parser modules; return handler enums.
- [x] TICKET-005.04 Expose a registry in src/processing/registry.py mapping format to callable parser.
- [x] TICKET-005.05 Run tests; refine messages; document supported types in docs/processing.md.

#### TICKET-006 — Plain Text & Markdown Parser
- [x] TICKET-006.01 Write failing tests in tests/processing/test_txt_md.py for reading .txt/.md, UTF-8 normalization, and output path in processed_documents/text/.
- [x] TICKET-006.02 Add tests for .md front-matter stripping (when present) and heading preservation.
- [x] TICKET-006.03 Implement src/processing/parsers/txt_md.py with safe filename creation and normalization utilities.
- [x] TICKET-006.04 Update mapping writer stub to capture original and processed paths (will be finalized in TICKET-012).
- [x] TICKET-006.05 Run tests; ensure negative case for invalid encoding handled with clear error.
- [x] TICKET-006.06 Refactor normalization helpers into src/processing/normalize.py for reuse.

#### TICKET-007 — Office Docs Parser (DOCX, PPTX)
- [x] TICKET-007.01 Write failing tests in tests/processing/test_office.py for docx paragraph extraction and pptx slide separation markers.
- [x] TICKET-007.02 Add tests for control character removal and newline normalization.
- [ ] TICKET-007.03 Implement src/processing/parsers/docx_pptx.py using python-docx and python-pptx; expose parse_docx and parse_pptx.
- [ ] TICKET-007.04 Run tests; validate counts of paragraphs/slides recorded for mapping later.
- [ ] TICKET-007.05 Refactor shared IO into src/processing/io.py to avoid duplication.

#### TICKET-008 — Spreadsheet & Tabular Parser (XLSX, CSV, TSV)
- [ ] TICKET-008.01 Write failing tests in tests/processing/test_tabular.py for xlsx sheet export to TSV-like text; csv/tsv normalization to tabs.
- [ ] TICKET-008.02 Add tests for header handling, empty cells, and special characters.
- [ ] TICKET-008.03 Implement src/processing/parsers/tabular.py using openpyxl and csv module; add sheet separators.
- [ ] TICKET-008.04 Run tests; verify sheet names and row counts are captured for mapping later.
- [ ] TICKET-008.05 Refactor delimiter normalization into src/processing/normalize.py.

#### TICKET-009 — PDF Text Extraction with OCR Fallback
- [ ] TICKET-009.01 Write failing tests in tests/processing/test_pdf.py for text extraction from searchable PDFs and OCR fallback on low-yield PDFs.
- [ ] TICKET-009.02 Add tests for page-level processing metadata and ocr_used flag behavior.
- [ ] TICKET-009.03 Implement src/processing/parsers/pdf.py using pdfminer.six/pypdf and pytesseract fallback per page with heuristic threshold.
- [ ] TICKET-009.04 Run tests; confirm OCR only triggers when coverage below threshold; add negative test for missing Tesseract binary.
- [ ] TICKET-009.05 Refactor image pre-processing for OCR into src/processing/images.py.

#### TICKET-010 — Image OCR (PNG/JPEG) and SVG Extraction
- [ ] TICKET-010.01 Write failing tests in tests/processing/test_image_svg.py for OCR of png/jpeg with language from config and SVG text node extraction.
- [ ] TICKET-010.02 Add tests for empty/low-quality images and non-textual SVGs (should produce empty output with no errors).
- [ ] TICKET-010.03 Implement src/processing/parsers/image_svg.py with pytesseract OCR and XML parsing for SVG <text> elements.
- [ ] TICKET-010.04 Run tests; validate outputs and error handling for unsupported image formats.
- [ ] TICKET-010.05 Document OCR configuration options in docs/processing.md.

#### TICKET-011 — Normalization Pipeline
- [ ] TICKET-011.01 Write failing tests in tests/processing/test_normalize.py for newline policy, whitespace trimming, and safe filename sanitation.
- [ ] TICKET-011.02 Add tests for simple header/footer stripping using explicit scanning functions (no regex).
- [ ] TICKET-011.03 Implement src/processing/normalize.py with reusable utilities; ensure deterministic output.
- [ ] TICKET-011.04 Run tests; confirm normalization applied consistently across parser outputs; refactor as needed.

#### TICKET-012 — Mapping Writer & Pipeline Error Handling
- [ ] TICKET-012.01 Write failing tests in tests/processing/test_mapping.py for mapping.json schema, checksums, timestamps, and per-file error capture.
- [ ] TICKET-012.02 Add tests for pipeline continuation on individual file failures; skipped/failed entries recorded.
- [ ] TICKET-012.03 Implement src/processing/mapping.py to write processed_documents/mapping.json; provide append/update behavior.
- [ ] TICKET-012.04 Implement src/processing/pipeline.py orchestrating detection → parse → normalize → write output and mapping entry.
- [ ] TICKET-012.05 Run tests; validate mapping correctness; refactor error taxonomy integration.

---

### Phase 2 — Provider Abstraction, Prompts, Attempt Runner, Adapters

#### TICKET-013 — Provider Interface & Registry
- [ ] TICKET-013.01 Write failing tests in tests/providers/test_interface.py verifying abstract ProviderClient API and error classes.
- [ ] TICKET-013.02 Add tests for provider registry resolving by provider name from config and rejecting unknown providers.
- [ ] TICKET-013.03 Implement src/providers/interface.py defining ProviderClient with prepare_prompt and call; define ProviderError hierarchy.
- [ ] TICKET-013.04 Implement src/providers/registry.py registering provider adapters by name.
- [ ] TICKET-013.05 Run tests; refactor for clarity; add type hints and docstrings.

#### TICKET-014 — Prompt Generator for plan.md, tickets.md, checklist.md
- [ ] TICKET-014.01 Write failing tests in tests/prompting/test_prompts.py asserting structure and constraints for plan/tickets/checklist prompts.
- [ ] TICKET-014.02 Add tests that processed document summaries with filename citations are included and length-bounded.
- [ ] TICKET-014.03 Implement src/prompting/generator.py producing PromptBundle with three prompts; include grounding and formatting constraints.
- [ ] TICKET-014.04 Implement src/prompting/summarizer.py to create short excerpts from processed_documents/text.
- [ ] TICKET-014.05 Run tests; adjust templates for determinism; refactor summarizer for readability.

#### TICKET-015 — Attempt Runner & Directory Management
- [ ] TICKET-015.01 Write failing tests in tests/attempts/test_runner.py to create attempt directories and persist prompts and outputs.
- [ ] TICKET-015.02 Add tests for attempt_manifest.json capturing parameters, seed, tokens, and errors.
- [ ] TICKET-015.03 Implement src/attempts/runner.py orchestrating per-provider attempts; write artifacts to {Provider}_{Developer}_{Model}/attempt_N/.
- [ ] TICKET-015.04 Implement src/attempts/artifacts.py helpers to write plan.md, tickets.md, checklist.md, and raw responses.
- [ ] TICKET-015.05 Run tests; validate idempotency for repeated attempt numbers; refactor path usage.

#### TICKET-016 — Anthropic Provider Adapter
- [ ] TICKET-016.01 Write failing tests in tests/providers/test_anthropic.py mocking httpx calls, retries on 429/5xx, and parameter mapping.
- [ ] TICKET-016.02 Implement src/providers/anthropic.py adapter with async httpx, reading API key from env; respect temperature/top_p/seed where supported.
- [ ] TICKET-016.03 Run tests; verify errors surface as ProviderError and recorded in attempt_manifest.json.
- [ ] TICKET-016.04 Add negative tests for missing/invalid API key and timeouts; refactor retry policy placement.

#### TICKET-017 — OpenRouter (OpenAI-Compatible) Adapter
- [ ] TICKET-017.01 Write failing tests in tests/providers/test_openrouter.py for header handling, model selection, and error propagation.
- [ ] TICKET-017.02 Implement src/providers/openrouter.py adapter calling OpenRouter chat/completions with configured headers and model.
- [ ] TICKET-017.03 Run tests; confirm artifact writing via Attempt Runner; refactor shared HTTP utilities.
- [ ] TICKET-017.04 Add negative tests for 401/403; ensure key isolation and redaction in logs.



#### TICKET-018 — LLM-as-Judge Engine & Rubric
- [ ] TICKET-018.01 Write failing tests in tests/evaluation/test_judge.py for producing task_relevance and documentation_relevance in [0.0,1.0] with rationale.
- [ ] TICKET-018.02 Add tests for weight configuration reading from config and default equality.
- [ ] TICKET-018.03 Implement src/evaluation/judge.py using ProviderClient or a dedicated judge adapter to score attempts.
- [ ] TICKET-018.04 Implement src/evaluation/schemas.py for evaluation.json schema and validation helpers.
- [ ] TICKET-018.05 Run tests; verify deterministic outputs under fixed seed; refactor prompts if necessary.

#### TICKET-019 — Ranking & Metadata Outputs
- [ ] TICKET-019.01 Write failing tests in tests/evaluation/test_ranking.py for weighted average calculation and tie-breakers.
- [ ] TICKET-019.02 Add tests for COMBINED_RESULTS/metadata.json contents including baseline path and weights.
- [ ] TICKET-019.03 Implement src/evaluation/ranking.py to compute scores and pick baseline; persist metadata.json.
- [ ] TICKET-019.04 Run tests; verify deterministic ranking with given inputs; refactor tie-breaker logic.

---

### Phase 4 — Combination Engine

#### TICKET-020 — Combination Strategy Engine
- [ ] TICKET-020.01 Write failing tests in tests/combination/test_engine.py ensuring combined plan/tickets/checklist are produced and cite sources.
- [ ] TICKET-020.02 Add tests for change proposals identification and acceptance criteria retention.
- [ ] TICKET-020.03 Implement src/combination/engine.py to compare baseline vs. others, draft improvements via LLM, and write combined docs.
- [ ] TICKET-020.04 Implement src/combination/trace.py to record citations and rationale per section.
- [ ] TICKET-020.05 Run tests; validate combined outputs exist and metadata contains rationale.

#### TICKET-021 — ID Normalization & Conflict Resolution
- [ ] TICKET-021.01 Write failing tests in tests/combination/test_ids.py for detecting duplicate ticket/checklist IDs across attempts.
- [ ] TICKET-021.02 Add tests for deterministic remapping strategy and metadata recording of mappings.
- [ ] TICKET-021.03 Implement src/combination/ids.py to normalize IDs and resolve collisions without regex; use explicit parsing helpers.
- [ ] TICKET-021.04 Run tests; confirm no duplicate IDs remain; refactor mapping for clarity.

---

### Phase 5 — CLI, Progress, Rate Limiting, Error Recovery, Reproducibility

#### TICKET-022 — CLI Commands & UX
- [ ] TICKET-022.01 Write failing tests in tests/cli/test_commands.py for subcommands run, process-docs, generate, evaluate, combine.
- [ ] TICKET-022.02 Add tests ensuring progress bars display expected stages and a final summary report is printed.
- [ ] TICKET-022.03 Implement src/cli.py subcommands wiring: run → full pipeline; others → respective modules.
- [ ] TICKET-022.04 Implement src/cli/progress.py using rich to display progress and stage timing.
- [ ] TICKET-022.05 Run tests; verify CLI exit codes and messages; refactor option parsing.

#### TICKET-023 — Rate Limiting & Retries
- [ ] TICKET-023.01 Write failing tests in tests/providers/test_rate_limits.py simulating 429/5xx and asserting exponential backoff and circuit breaker behavior.
- [ ] TICKET-023.02 Implement src/providers/rate_limit.py with token bucket implementation per provider.
- [ ] TICKET-023.03 Implement src/providers/retry.py with tenacity/backoff policies; integrate with provider adapters.
- [ ] TICKET-023.04 Run tests; verify telemetry includes retry counts and breaker events.

#### TICKET-024 — Error Taxonomy & Propagation
- [ ] TICKET-024.01 Write failing tests in tests/errors/test_errors.py for specific error types and mapping to exit codes/messages.
- [ ] TICKET-024.02 Implement src/errors.py with ParsingError, ProviderError, RateLimitError, JudgeError, CombineError and helpers.
- [ ] TICKET-024.03 Integrate error types across processing, providers, judge, and combination modules.
- [ ] TICKET-024.04 Run tests; verify actionable user messages and preservation of partial artifacts.

#### TICKET-025 — Reproducibility & Manifests
- [ ] TICKET-025.01 Write failing tests in tests/manifests/test_repro.py for seeds/params/prompts/checksums presence in attempt_manifest.json.
- [ ] TICKET-025.02 Implement dry-run mode in src/cli.py that prints planned actions without network calls.
- [ ] TICKET-025.03 Ensure attempt manifest completeness in src/attempts/runner.py and artifacts.
- [ ] TICKET-025.04 Run tests; verify reproducibility notes stored and dry-run behavior.

---

### Phase 6 — Testing, CI/CD, Containerization, Docs, Observability

#### TICKET-026 — Parser Unit Tests & Fixtures
- [ ] TICKET-026.01 Create fixtures in tests/fixtures/{txt,md,docx,pptx,xlsx,csv,tsv,pdf,images,svg}/ with tiny samples.
- [ ] TICKET-026.02 Write comprehensive unit tests across all parser modules and normalization utilities.
- [ ] TICKET-026.03 Run tests; ensure coverage includes positive and negative cases; refactor flaky tests.
- [ ] TICKET-026.04 Add documentation in docs/processing.md explaining fixture design.

#### TICKET-027 — Mocked Provider & Attempt Runner Tests
- [ ] TICKET-027.01 Create golden files in tests/golden/ for plan.md, tickets.md, checklist.md.
- [ ] TICKET-027.02 Write integration tests for Attempt Runner with respx mocks covering success and error paths.
- [ ] TICKET-027.03 Run tests; validate artifacts and manifests; ensure retries recorded on transient failures.
- [ ] TICKET-027.04 Refactor Attempt Runner for testability if required (dependency injection of HTTP clients).

#### TICKET-028 — Judge, Ranking, and Combination Tests
- [ ] TICKET-028.01 Write tests covering judge scoring edge cases, ranking tie-breakers, and combination output validation.
- [ ] TICKET-028.02 Run tests; verify metadata rationale completeness and ID uniqueness checks.
- [ ] TICKET-028.03 Add additional negative tests (e.g., missing attempt docs) for combination error handling.

#### TICKET-029 — CI Setup (Lint/Type/Coverage)
- [ ] TICKET-029.01 Add pyproject.toml entries for ruff/flake8, mypy, pytest, and coverage; set thresholds.
- [ ] TICKET-029.02 Create .github/workflows/ci.yml running lint, type-check, tests, and coverage upload.
- [ ] TICKET-029.03 Ensure venv caching strategy in CI and matrix for Python 3.11/3.12.
- [ ] TICKET-029.04 Document CI requirements in README and badges.

#### TICKET-030 — Containerization (Dockerfile) & Local Run Docs
- [ ] TICKET-030.01 Write Dockerfile with multi-stage build, optional Tesseract layer, and small runtime image.
- [ ] TICKET-030.02 Add docker-compose.example.yml demonstrating volume mounts for source docs and config.
- [ ] TICKET-030.03 Write tests/scripts to smoke-run the container with a tiny fixture set (no network by default).
- [ ] TICKET-030.04 Update README with Docker usage instructions and environment variables.

#### TICKET-031 — User Documentation & Examples
- [ ] TICKET-031.01 Write docs/USAGE.md with end-to-end instructions and troubleshooting matrix.
- [ ] TICKET-031.02 Provide examples/config.example.yaml and examples/minimal_input set.
- [ ] TICKET-031.03 Verify examples by running `process-docs` then `generate --dry-run` and capture outputs in docs/examples.md.
- [ ] TICKET-031.04 Final pass on README; ensure alignment with CLI and config; spellcheck and link check.
