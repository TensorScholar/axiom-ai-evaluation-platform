# Task 009 Report — Trace Import and Failure Conversion

## Summary

Expanded and implemented task `009` as in-memory trace import records, failed-trace selection, and conversion of selected failures into domain test cases.

## Spec Update

The previously incomplete task `009` spec was replaced under explicit user approval with concrete structure, behavior, forbidden scope, verification, and acceptance criteria.

## Changes

- Added `TraceRecord` and `TraceBatch` Pydantic models.
- Added `import_trace_batch`.
- Added `select_failed_traces`.
- Added `trace_failure_to_test_case`.
- Added focused tests in `tests/traces/test_trace_import.py`.

## Validation

- `python3 -m pytest tests/traces` passed with 10 tests.
- `python3 -m compileall app` passed.
- `python3 scripts/axiom_verify.py --task 009` is the task verifier command used in this environment because `python` is not available on PATH.
- Verification ledger: `.axiom/verification/task_009_verification.json`.
- Verifier overall status: `passed`.
- Protected file checksum check: `passed`.

## Self-Audit

- Implemented only task `009`.
- Did not implement future task behavior.
- Satisfied all task `009` acceptance criteria.
- Did not change acceptance criteria after implementation.
- Added tests for introduced behavior.
- Did not weaken or delete tests.
- Ran the required verifier script with the available Python runtime.
- JSON verification ledger exists.
- Task report exists.
- Verifier exit code is 0.
- Did not edit protected files.
- Did not add dependencies.
- Did not add forbidden infrastructure.
- Did not add external trace connectors, file watchers, persistence, provider calls, evaluation execution, regression execution, CLI, or frontend.
