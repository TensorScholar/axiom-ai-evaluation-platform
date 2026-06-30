# Task 020 Report — Local Eval CLI

## Summary

Implemented `axiom eval` for running a local evaluation from JSON fixtures with the fake provider and writing an evaluation run result file.

## Changes

- Added `specs/020_local_eval_cli.spec.md`.
- Added `app/local_eval.py`.
- Extended `app.cli` with `eval --dataset-file --provider-file --output-file`.
- Added focused tests in `tests/cli/test_local_eval_cli.py`.

## Validation

- `python3 -m pytest tests/cli` passed with 9 tests.
- `python3 -m compileall app` passed.
- Verification ledger: `.axiom/verification/task_020_verification.json`.

## Self-Audit

- Implemented only roadmap task `020`.
- Did not edit protected files.
- Did not add dependencies.
- Did not add forbidden infrastructure.
- Did not add real provider calls, persistence, packaging entry points, external services, or trace import behavior.
- Added tests for introduced behavior.
- Did not weaken or delete tests.
