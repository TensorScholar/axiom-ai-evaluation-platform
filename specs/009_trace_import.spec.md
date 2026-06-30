# Spec 009 — Trace Import and Failure Conversion

## Objective

Create minimal trace import records and helpers that convert selected agent or LLM app failures into evaluation test cases.

This task defines in-memory parsing and conversion only. It must not implement persistence, external trace connectors, provider calls, evaluation execution, regression execution, CLI behavior, or frontend behavior.

## Required Structure

```text
app/traces/
  __init__.py
  importers.py
  models.py

tests/traces/
  test_trace_import.py
```

## Required Behavior

Trace records must:

- be Pydantic models,
- include `id`, `inputs`, `output`, `error_message`, and `metadata`,
- reject blank ids,
- reject empty inputs,
- require either output or error message,
- produce deterministic JSON-compatible dumps.

Trace batches must:

- be Pydantic models,
- include `records`,
- reject empty record lists,
- reject duplicate trace ids.

Trace import helpers must:

- import trace batches from a JSON-compatible payload shaped as `{"records": [...]}`,
- reject invalid payload shapes with clear errors,
- select failed traces when `error_message` is present or `metadata.failed` is true,
- convert selected failed traces into domain `TestCase` records,
- reject conversion of non-failed traces.

Required helpers:

- `import_trace_batch(payload) -> TraceBatch`
- `select_failed_traces(batch) -> list[TraceRecord]`
- `trace_failure_to_test_case(record, test_case_id, dataset_id, name=None, expected_output=None) -> TestCase`

## Forbidden

Do not implement:

- external trace connectors,
- file watchers,
- persistence,
- provider API calls,
- evaluation execution,
- regression execution,
- CLI,
- frontend,
- Kafka,
- Kubernetes,
- Celery,
- Qdrant,
- event sourcing,
- microservices.

## Verification

Run:

```bash
python scripts/axiom_verify.py --task 009
```

## Acceptance Criteria

- [ ] Trace records exist and validate required fields.
- [ ] Trace batches reject empty records and duplicate ids.
- [ ] Trace import rejects invalid payload shapes.
- [ ] Failed trace selection is deterministic.
- [ ] Failed traces convert into domain `TestCase` records.
- [ ] Non-failed traces cannot be converted as failures.
- [ ] `tests/traces` coverage exists for introduced behavior.
- [ ] `python scripts/axiom_verify.py --task 009` passes.
- [ ] `.axiom/verification/task_009_verification.json` exists.
- [ ] `.axiom/reports/task_009_report.md` exists.
- [ ] no forbidden infrastructure is introduced.
- [ ] no future milestone is implemented early.
