## Automated LLM-Based Project Planning & Documentation Generation System — Technical Plan

### 1) Executive Summary
This document defines the architecture, implementation strategy, and operational plan for a system that ingests a user’s task description and a directory of heterogeneous source documents, converts them to text, invokes multiple LLM providers/agents to generate project documents (plan.md, tickets.md, checklist.md), evaluates outputs with LLM-as-judge, ranks results, and produces a combined final set of documents.

### 2) Goals and Non-Goals
- Goals
  - End-to-end automation from input collection to combined final outputs
  - Deterministic directory structure and traceability for all artifacts
  - Support for multiple providers and multiple attempts per provider
  - Robust parsing for varied document formats with OCR fallback
  - Quality evaluation based on task relevance and documentation relevance
  - Reproducible runs with configuration and seeding controls
- Non-Goals
  - Building a GUI beyond a CLI/progress reporting layer (initial phase)
  - Replacing upstream provider SDKs; we will wrap official clients or CLIs

### 3) User Workflow (Happy Path)
1. User provides: (a) task description text; (b) path to source documents directory.
2. System converts all documents to plain text and stores them in processed_documents/ with filename mapping.
3. User selects one or more LLM configurations (provider, developer, model) and number of attempts per configuration.
4. System generates prompts and executes LLM calls/CLI agents concurrently with retries and rate limiting.
5. System stores per-attempt outputs: plan.md, tickets.md, checklist.md.
6. LLM-as-judge evaluates outputs on task relevance and documentation relevance.
7. System ranks all attempts and selects the top attempt as baseline.
8. System combines best sections from other attempts into enhanced final outputs.
9. Final documents and metadata are written to COMBINED_RESULTS/.

### 4) High-Level Architecture
- CLI/Orchestrator
  - Entry point, argument parsing, progress display, run lifecycle control.
- Config & Secrets Manager
  - Loads YAML/TOML/JSON config, environment variables for API keys, weights, concurrency, seeds.
- Document Processing Service
  - Format detection, parsing, OCR, normalization; writes .txt files and mapping for traceability.
- Provider Abstraction Layer
  - Unified interface for providers/agents (Anthropic, Claude Code, OpenRouter, OpenCode, RovoDev, QwenCode, etc.).
- Attempt Runner
  - For each provider configuration and attempt, generates prompts, executes calls, persists artifacts.
- Judge/Evaluation Engine
  - LLM-based scoring of task relevance and documentation relevance.
- Ranking & Selection Engine
  - Weighted average scoring, ranking across all attempts.
- Combination Engine
  - Uses highest-ranked attempt as baseline and selectively merges improvements from others.
- Storage Manager
  - Creates and manages directory structures and metadata artifacts.
- Telemetry & Logging
  - Structured logs, progress events, error tracking, run manifest.

### 5) Directory Structure (Outputs)
- processed_documents/
  - text/ … one .txt per source file
  - mapping.json … original → processed filename mapping with metadata
- {Provider}_{Developer}_{Model}/
  - attempt_1/
    - plan.md, tickets.md, checklist.md, attempt_manifest.json
  - attempt_2/ …
- COMBINED_RESULTS/
  - plan.md, tickets.md, checklist.md
  - metadata.json (ranking results, weights, combination rationale)

### 6) Configuration
- Files: config.yaml (preferred) or config.toml/json
- Example (abbreviated):
  - input:
    - task_description_path: path/to/task.txt
    - source_dir: path/to/source_docs
  - processing:
    - ocr: auto|always|never
    - ocr_engine: tesseract|vision_api
    - language: eng
  - providers:
    - - provider: Anthropic
        developer: Anthropic
        model: Claude-3.5-Sonnet
        attempts: 2
        max_concurrency: 2
        api_key_env: ANTHROPIC_API_KEY
      - provider: OpenRouter
        developer: OpenAI
        model: gpt-4.1
        attempts: 2
        max_concurrency: 2
        api_key_env: OPENROUTER_API_KEY
  - generation:
    - temperature: 0.2
    - top_p: 1.0
    - seed: 7
    - max_tokens: 8000
  - evaluation:
    - weights:
      - task_relevance: 1.0
      - documentation_relevance: 1.0
    - judge_provider: Anthropic
    - judge_model: Claude-3.5-Sonnet
  - rate_limits:
    - Anthropic: { rpm: 30, rps: 2 }
    - OpenRouter: { rpm: 60, rps: 3 }
  - logging:
    - level: INFO
    - format: json
  - output:
    - base_dir: .

- Secrets via environment variables (e.g., ANTHROPIC_API_KEY, OPENROUTER_API_KEY). No secrets in VCS.

### 7) Document Processing Pipeline
- Supported Formats & Libraries (Python)
  - txt, md: basic IO
  - docx: python-docx
  - xlsx: openpyxl
  - csv/tsv: csv module; normalize delimiters to tabs for TSV output text
  - pdf: pypdf or pdfminer.six; fallback to OCR per page using pytesseract if extraction fails or yields low text coverage
  - pptx: python-pptx
  - png/jpeg: OCR via pytesseract (requires system Tesseract) or cloud Vision API option
  - svg: xml.etree.ElementTree to extract textual nodes
- Steps
  - Detect format → parse to text → normalize (UTF-8, whitespace, page headers/footers) → write to processed_documents/text/<safe_name>.txt
  - Write mapping.json entries: original_path, processed_relpath, mime/format, pages (if applicable), parser, ocr_used, timestamps, checksum.
  - Error Handling: capture parser errors per file, mark failed in mapping.json, continue pipeline.

### 8) Provider Integration & Execution
- Abstraction: ProviderClient interface
  - prepare_prompt(task, processed_docs_index, attempt_id) → PromptBundle
  - call(prompt_bundle, params) → { plan.md, tickets.md, checklist.md, raw_response_meta }
- Providers
  - Anthropic API
  - Claude Code (where available, CLI or API wrapper)
  - OpenRouter (routing to e.g., OpenAI-compatible models)
  - Coding Agents: OpenCode, RovoDev, QwenCode via CLI where applicable
- Concurrency & Rate Limiting
  - Async HTTP client (httpx) with bounded semaphores per provider
  - Token bucket or leaky bucket limiter per provider; exponential backoff (tenacity/backoff) on 429/5xx
- Reproducibility
  - Set seed, temperature/top_p where supported; persist all request parameters in attempt_manifest.json
- Error Recovery
  - Retries with jitter, circuit breaker on repeated failures; partial artifacts are saved with error notes

### 9) Prompt Generation
- Inputs
  - task_description (text)
  - processed document summaries (short excerpts + filenames)
- Deliverables (one prompt each or a multi-part prompt with explicit sections):
  - plan.md: architecture, components, data flow, timeline, implementation details, risks, testing, deployment
  - tickets.md: ticket IDs, descriptions, acceptance criteria, dependencies
  - checklist.md: per-ticket granular tasks with checkboxes; task IDs formatted {ticket_id}.{task_id}; emphasize TDD
- Grounding
  - Instruct models to cite source filenames (from processed docs) when using information; maintain traceability via in-text references like [source: filename.txt]
- Output Strictness
  - Enforce markdown headings and file-specific structure; instruct to avoid adding unrelated files; require utf-8/plain markdown only

### 10) Attempt Management
- For each provider configuration:
  - Create directory: {Provider}_{Developer}_{Model}/attempt_N/
  - Save prompts, parameters, raw responses (optional), and final plan.md, tickets.md, checklist.md
  - attempt_manifest.json captures: timestamps, seed, temperatures, token counts, rate-limit events, errors

### 11) Evaluation (LLM-as-Judge)
- Two Criteria
  - Task Relevance (0.0–1.0): Fitness to the original task description
  - Documentation Relevance (0.0–1.0): Incorporation of information from processed documents
- Judge Prompt (abbrev rubric)
  - Provide task description + generated docs; ask for two normalized scores and rationale
- Output
  - evaluation.json per attempt: { task_relevance, documentation_relevance, rationale }

### 12) Ranking & Selection
- Weighted average per attempt: (task_relevance * w1 + documentation_relevance * w2) / (w1 + w2)
- Rank attempts across all providers; tie-breakers: lower temperature result first, then earliest timestamp
- Persist ranking in COMBINED_RESULTS/metadata.json

### 13) Combination Strategy
- Baseline = highest-ranked attempt’s three documents
- Use an LLM to:
  - Compare baseline vs. other attempts and identify beneficial sections (architecture clarity, test detail, risk mitigation, etc.)
  - Propose changes with citations to attempt paths
  - Produce enhanced combined plan.md, tickets.md, checklist.md
- Constraints
  - Maintain consistent IDs across tickets/checklists; if collisions occur, map additional items to new suffixes
  - Preserve TDD emphasis, dependency mapping, and traceability notes

### 14) Final Output Generation
- Create COMBINED_RESULTS/
  - plan.md, tickets.md, checklist.md (enhanced)
  - metadata.json: ranking table, weights, judge model, selection rationale, combination diffs summary

### 15) Technical Requirements & Cross-Cutting Concerns
- Error Handling & Logging
  - Use structured JSON logs with levels (DEBUG/INFO/WARN/ERROR)
  - Error taxonomy: ParsingError, ProviderError, RateLimitError, JudgeError, CombineError
  - Persist per-file/per-attempt errors in manifests
- Progress & UX
  - CLI with progress bars/spinners, per-stage counters, and summary report; dry-run mode for planning
- Concurrency
  - Async orchestrator with bounded worker pools; cautious defaults; user-overridable in config
- Seeds & Determinism
  - Record seeds and all parameters; store prompts and checksums; note provider limitations where seeds are advisory
- Security
  - API keys only via environment; redact secrets in logs; optional local-only mode for sensitive docs
- Resource Mgmt
  - Size limits for documents; chunking/summary extraction for very large inputs

### 16) Dependencies (Proposed)
- Runtime
  - Python 3.11+
  - httpx (async HTTP)
  - pydantic (config/schema validation)
  - pyyaml or tomli/tomllib (config)
  - tenacity or backoff (retries)
  - rich (CLI progress)
  - python-docx, openpyxl, python-pptx
  - pypdf or pdfminer.six, pdfplumber (optional)
  - pytesseract (with system Tesseract) or cloud Vision API client
  - Pillow (image IO)
  - lxml or built-in xml.etree for SVG
- Testing
  - pytest, pytest-asyncio, responses/httpretty or respx

### 17) Testing Strategy
- Unit Tests
  - Parsers (by format), text normalization, mapping.json generation
  - Provider adapter behavior using mocked HTTP/CLI
  - Prompt generator: structure and constraints
- Integration Tests
  - End-to-end single provider with mocked LLM returning deterministic outputs
  - Judge and ranking pipeline with golden files
- End-to-End (Optional/Flagged)
  - Smoke with real provider (opt-in via env), low token limits
- Quality Gates
  - Lint/type checks, test coverage thresholds, reproducible run manifest verification

### 18) Deployment & Operations
- Local Execution
  - Python venv, CLI entrypoint, .env support
- Containerization
  - Minimal Docker image with system Tesseract optional layer; mount source_docs volume
- CI/CD
  - Lint, tests, packaging, release tags; optional integration tests with mock providers
- Observability
  - Structured logs; optional OpenTelemetry exporters

### 19) CLI Design (Initial)
- Commands
  - run: executes full pipeline
  - process-docs: only run conversion pipeline
  - generate: run providers/attempts only
  - evaluate: run judge/ranking only
  - combine: run combination only
- Flags
  - --config, --task, --source-dir, --providers, --attempts, --concurrency, --ocr, --seed, --temp, --dry-run, --verbose

### 20) Implementation Phases & Milestones
- Phase 0: Project skeleton, venv setup, config schema, logging/telemetry scaffolding
- Phase 1: Document processing pipeline with mapping and error handling
- Phase 2: Provider abstraction and at least two provider adapters; attempt runner; basic prompts
- Phase 3: Judge/evaluation engine; ranking & metadata outputs
- Phase 4: Combination engine; ID normalization; final outputs
- Phase 5: CLI polish; progress reporting; robust retries and rate limiting
- Phase 6: Test hardening, fixtures/golden files, performance tuning, docs

### 21) Code & Style Guidelines
- Python venv required; do not rely on global site-packages
- Avoid list comprehensions; use explicit for-loops for clarity
- Avoid regular expressions for pattern matching in app logic; implement explicit parsing helpers
- Explicit error classes; no silent excepts; always log and propagate context
- No secrets in repos; use environment variables; redact in logs

### 22) Risk Register (Selected)
- OCR accuracy variability → configurable engine, language packs, and page-level fallbacks
- Provider rate limits → per-provider limiter, adaptive backoff, circuit breakers
- Reproducibility gaps across providers → thorough manifests and parameter capture
- Large documents → chunking, summarization, and size caps

### 23) Acceptance Criteria (System-Level)
- Supports all listed formats; produces .txt with mapping.json
- Generates plan.md, tickets.md, checklist.md for each attempt across at least two providers
- Produces evaluation scores and ranks attempts
- COMBINED_RESULTS contains enhanced merged documents and metadata with rationale
- All artifacts reproducible from a single config and source directory

