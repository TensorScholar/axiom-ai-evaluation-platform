# Spec 061 — Regression API Endpoints

## Objective

Add FastAPI endpoints for regression suites and gate results using existing typed models.

This task must not execute external providers, run regression suites, add background jobs, add authentication, or add frontend behavior.

## Required Behavior

Regression suite API behavior must:

- expose create, list, and get endpoints for regression suites,
- persist regression suites through `SQLiteStore`,
- use `RegressionSuite` as the typed request and response boundary,
- return `404` for missing suites,
- return `409` for duplicate creates,
- return FastAPI validation errors for invalid payloads.

Gate result API behavior must:

- expose an endpoint that derives a `GateResult` from an `EvaluationRunSummary`,
- support `min_pass_rate` and `max_error_rate` thresholds,
- return deterministic typed gate result JSON,
- return validation errors for invalid thresholds,
- avoid executing providers or regression reruns implicitly.

## Verification

Run:

```bash
python3 -m pytest tests/api tests/cli/test_ci_gate.py
python3 -m compileall app
```

## Acceptance Criteria

- [ ] Regression suite API endpoints create, list, and get persisted suites.
- [ ] Missing regression suites return `404`.
- [ ] Duplicate regression suite creates return `409`.
- [ ] Invalid regression suite payloads return FastAPI validation errors.
- [ ] Gate result endpoint derives typed deterministic gate result JSON from summaries.
- [ ] Gate result endpoint respects threshold parameters.
- [ ] Invalid gate thresholds return validation errors.
- [ ] Route-level tests use a temporary SQLite store.
- [ ] Verification evidence exists in `.axiom/verification/task_061_verification.json`.
- [ ] Task report exists in `.axiom/reports/task_061_report.md`.
