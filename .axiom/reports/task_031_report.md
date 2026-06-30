# Task 031 Report — Run History Queries

## Summary

Implemented deterministic run history queries over the SQLite persistence store.

## Changes

- Added `specs/031_run_history_queries.spec.md`.
- Added `FailedSampleRecord` and `RegressionCandidate` query models.
- Added filtered run queries to `SQLiteStore`.
- Added failed sample and regression candidate query helpers.
- Added focused tests in `tests/persistence/test_run_history_queries.py`.

## Validation

- `python3 -m pytest tests/persistence` passed with 8 tests.
- `python3 -m compileall app` passed.
- Verification ledger: `.axiom/verification/task_031_verification.json`.

## Self-Audit

- Implemented only roadmap task `031`.
- Did not edit protected files.
- Did not add dependencies.
- Did not add forbidden infrastructure.
- Did not add migrations, web APIs, provider calls, auth, deployment, or external services.
- Added tests for introduced behavior.
- Did not weaken or delete tests.
