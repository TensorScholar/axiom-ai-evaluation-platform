# Spec 060 — Evaluation API Endpoints

## Objective

Add FastAPI endpoints for local project, dataset, and evaluation run records using the existing domain and SQLite persistence layers.

This task must not add a frontend, authentication, provider execution, background jobs, or regression endpoints.

## Required Behavior

API behavior must:

- expose create, list, and get endpoints for projects,
- expose create, list, and get endpoints for datasets,
- expose create, list, and get endpoints for evaluation runs,
- support deterministic evaluation run listing with optional project, dataset, and status filters,
- use typed domain/evaluation models as request and response boundaries,
- persist records through `SQLiteStore`,
- return `404` for missing records,
- return `409` for duplicate creates,
- return FastAPI validation errors for invalid payloads,
- keep `/health` behavior unchanged.

## Verification

Run:

```bash
python3 -m pytest tests/test_health.py tests/api
python3 -m compileall app
```

## Acceptance Criteria

- [ ] Project API endpoints create, list, and get persisted project records.
- [ ] Dataset API endpoints create, list, and get persisted dataset records.
- [ ] Evaluation run API endpoints create, list, get, and filter persisted run records.
- [ ] Missing records return `404`.
- [ ] Duplicate creates return `409`.
- [ ] Invalid payloads return FastAPI validation errors.
- [ ] Health endpoint behavior remains unchanged.
- [ ] Route-level tests use a temporary SQLite store.
- [ ] Verification evidence exists in `.axiom/verification/task_060_verification.json`.
- [ ] Task report exists in `.axiom/reports/task_060_report.md`.
