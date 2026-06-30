# Spec 030 — SQLite Persistence

## Objective

Add local SQLite persistence for core AXIOM records using SQLAlchemy.

This task must not add external services, migrations, web APIs, auth, deployment, or distributed infrastructure.

## Required Behavior

Persistence must support create/read/list for:

- `Project`
- `Dataset`
- `TestCase`
- `EvaluationRunRecord` including sample results
- `RegressionSuite`

Implementation constraints:

- use SQLAlchemy Core with SQLite,
- keep storage local and deterministic,
- serialize existing Pydantic/domain records as JSON-compatible payloads where useful,
- reject duplicate primary keys through database constraints,
- return typed domain records from reads,
- return records ordered by id for list operations.

## Verification

Run:

```bash
python3 -m pytest tests/persistence
python3 -m compileall app
```

## Acceptance Criteria

- [ ] SQLite schema initializes locally.
- [ ] Projects can be saved, loaded, and listed.
- [ ] Datasets can be saved, loaded, and listed.
- [ ] Test cases can be saved, loaded, and listed.
- [ ] Evaluation runs including sample results can be saved, loaded, and listed.
- [ ] Regression suites can be saved, loaded, and listed.
- [ ] Duplicate primary keys are rejected.
- [ ] Verification evidence exists in `.axiom/verification/task_030_verification.json`.
- [ ] Task report exists in `.axiom/reports/task_030_report.md`.
