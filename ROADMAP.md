# AXIOM Roadmap

## Current Baseline

AXIOM v0.5 has a verified in-memory foundation:

- FastAPI app scaffold and health endpoint.
- Typed domain records for projects, datasets, test cases, rubrics, and run identifiers.
- Evaluation run lifecycle records and status transitions.
- Provider adapter protocol and deterministic fake provider.
- Deterministic metrics.
- Structured judge abstraction and scripted judge.
- Judge reliability signals.
- Regression suite records and rerun plans.
- CLI gate over precomputed regression results.
- Trace import records and failure conversion.

The next roadmap turns this foundation into an end-to-end local evaluation platform before adding persistence, real provider integrations, and deployment concerns.

## Principles

- Keep AXIOM a modular monolith.
- Prefer deterministic, local-first behavior before external services.
- Make every new capability executable through tests before integrating it into higher layers.
- Keep provider, judge, metric, trace, and regression boundaries explicit.
- Treat LLM judges as signals, not objective truth.
- Avoid infrastructure until persistence, scale, and deployment specs require it.

## Phase 1 — Local Execution Core

### 010 — In-Memory Evaluation Runner

Implement a synchronous local runner that executes domain test cases through a provider adapter, records sample-level results, applies deterministic metrics, and returns an evaluation run record.

Acceptance:

- Runs a non-empty list of `TestCase` records.
- Builds deterministic prompts from test case inputs.
- Calls a `ProviderAdapter`.
- Records provider text, metadata, and metric results per sample.
- Converts provider exceptions into errored sample records.
- Preserves evaluation run lifecycle transitions.
- Adds focused tests and verification evidence.

### 011 — Metric Registry

Create a typed registry that maps metric names/configurations to deterministic metric functions.

Acceptance:

- Supports exact match, regex, numeric tolerance, and JSON-schema-style metrics.
- Rejects unknown metric names and invalid configs.
- Produces deterministic metric result lists.

### 012 — Dataset-Level Summary

Create summary records over sample results.

Acceptance:

- Calculates total, succeeded, errored, pass rate, and failed metric counts.
- Produces JSON-compatible dumps.
- Does not hide individual sample failures.

## Phase 2 — CLI Usability

### 020 — Local Eval CLI

Add CLI support for running a local evaluation from JSON fixtures using the fake provider.

Acceptance:

- Reads dataset and scripted-provider fixture files.
- Runs the local evaluation runner.
- Writes a JSON result file.
- Exits nonzero on invalid input.

### 021 — Gate CLI Integration

Connect evaluation summaries to the existing gate command.

Acceptance:

- Converts evaluation summaries into gate result files.
- Preserves existing `gate --result-file` behavior.
- Adds tests for passing and failing gates.

## Phase 3 — Persistence

### 030 — SQLite Persistence

Add local SQLite persistence for projects, datasets, test cases, evaluation runs, sample results, and regression suites.

Acceptance:

- Uses SQLAlchemy only at this phase.
- Provides repository interfaces with deterministic tests.
- Supports create/read/list for core records.

### 031 — Run History Queries

Add query helpers for recent runs, failed samples, and regression candidates.

Acceptance:

- Filters by project, dataset, status, and time.
- Includes tests for ordering and empty results.

## Phase 4 — Real Provider Integrations

### 040 — OpenAI Provider Adapter

Add a real provider adapter behind the existing provider protocol.

Acceptance:

- Requires explicit configuration.
- Does not read secrets implicitly from tests.
- Uses typed request/response boundaries.
- Keeps fake provider as the default test path.

### 041 — Provider Failure Taxonomy

Normalize provider failures into typed error categories.

Acceptance:

- Separates validation, auth, rate limit, timeout, and unknown failures.
- Converts failures into sample-level error records.

## Phase 5 — Trace and Regression Workflow

### 050 — Trace File Import CLI

Expose trace import from local JSON files.

Acceptance:

- Imports trace batches.
- Selects failed traces.
- Converts selected failures into test cases or regression cases.

### 051 — Regression Promotion Workflow

Create a local workflow to promote failed samples into regression suites.

Acceptance:

- Deduplicates promoted cases.
- Preserves source run metadata.
- Produces reviewable JSON output.

## Phase 6 — API Surface

### 060 — Evaluation API Endpoints

Add FastAPI endpoints for local project, dataset, and run records after persistence exists.

Acceptance:

- No frontend yet.
- API wraps existing domain and persistence layers.
- Includes route-level tests.

### 061 — Regression API Endpoints

Add endpoints for regression suites and gate results.

Acceptance:

- Keeps API payloads typed and deterministic.
- Does not execute external providers implicitly.

## Phase 7 — Release Readiness

### 070 — Packaging

Add packaging metadata and console scripts.

Acceptance:

- Defines installable package metadata.
- Provides a stable `axiom` console command.
- Documents local installation.

### 071 — CI Workflow

Add a minimal GitHub Actions workflow.

Acceptance:

- Runs tests and compile checks.
- Avoids deployment and external service dependencies.

### 072 — Documentation and Examples

Add runnable examples for fake-provider evaluation, trace import, regression promotion, and CI gate usage.

Acceptance:

- Examples run locally without secrets.
- Documentation matches tested behavior.

## Later, Explicitly Not Now

- Distributed execution.
- Kubernetes or Terraform.
- Multi-tenant auth.
- Web dashboard.
- Enterprise observability.
- Custom model training.
- Semantic caching for official evals.
