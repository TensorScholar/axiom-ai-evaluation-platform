# Spec 002 — Evaluation Run Lifecycle Records

## Objective

Create minimal, deterministic in-memory records for evaluation run lifecycle state, sample-level results, and reproducible metadata.

This task defines lifecycle validation only. It must not execute evaluations, call providers, compute metrics, invoke judges, persist data, import traces, or expose CLI behavior.

## Required Structure

```text
app/evaluations/
  __init__.py
  lifecycle.py
  models.py

tests/evaluations/
  test_lifecycle.py
```

## Required Behavior

Evaluation statuses must be explicit:

- `pending`
- `running`
- `completed`
- `failed`

Allowed transitions:

- `pending -> running`
- `running -> completed`
- `running -> failed`

All other transitions must be rejected.

Reproducible metadata must:

- be a Pydantic model,
- include `spec_version`, `code_version`, `dataset_fingerprint`, `seed`, and `parameters`,
- reject blank required string fields,
- reject negative seeds,
- allow JSON-compatible parameter values,
- produce deterministic JSON-compatible dumps.

Sample-level result records must:

- be Pydantic models,
- reference a `TestCaseId`,
- support outcomes `succeeded` and `errored`,
- require non-empty error messages for errored samples,
- reject error messages for succeeded samples,
- include JSON-compatible output and metadata fields.

Evaluation run records must:

- be Pydantic models,
- reference `EvaluationRunId`, `ProjectId`, and `DatasetId`,
- include status, reproducible metadata, and sample results,
- start in `pending` when created by `new_evaluation_run`,
- transition through pure helper functions without mutating the previous record.

Required helpers:

- `can_transition(current, next_status) -> bool`
- `transition_run(run, next_status) -> EvaluationRunRecord`
- `new_evaluation_run(...) -> EvaluationRunRecord`
- `record_sample_result(run, result) -> EvaluationRunRecord`

`record_sample_result` must only accept sample results while the run is `running`.

## Forbidden

Do not implement:

- database models,
- repositories,
- evaluation execution,
- provider adapters,
- metrics,
- judges,
- regression suites,
- CLI,
- frontend,
- trace import,
- Kafka,
- Kubernetes,
- Celery,
- Qdrant,
- event sourcing,
- microservices.

## Verification

Run:

```bash
python scripts/axiom_verify.py --task 002
```

## Acceptance Criteria

- [ ] Evaluation status enum exists.
- [ ] Allowed lifecycle transitions are enforced.
- [ ] Invalid lifecycle transitions are rejected.
- [ ] Reproducible metadata validates required fields and JSON-compatible parameters.
- [ ] Sample result records validate outcomes and errors.
- [ ] Evaluation run records are immutable-by-helper and deterministic to dump.
- [ ] `tests/evaluations` coverage exists for introduced behavior.
- [ ] `python scripts/axiom_verify.py --task 002` passes.
- [ ] `.axiom/verification/task_002_verification.json` exists.
- [ ] `.axiom/reports/task_002_report.md` exists.
- [ ] no forbidden infrastructure is introduced.
- [ ] no future milestone is implemented early.
