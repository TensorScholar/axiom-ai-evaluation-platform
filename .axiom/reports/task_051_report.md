# Task 051 Report — Regression Promotion Workflow

## Summary

Added a local regression promotion workflow that converts failed evaluation samples into reviewable regression suite JSON.

## Changes

- Added `specs/051_regression_promotion_workflow.spec.md`.
- Added `app.regression.promotion` for deterministic promotion from evaluation run records plus source test cases.
- Exported promotion APIs from `app.regression`.
- Added `promote-regressions` CLI subcommand.
- Added regression promotion and CLI tests.

## Validation

- `python3 scripts/axiom_verify.py --task 051` returned `Unknown task: 051` because the protected verifier only defines tasks `000` through `009`.
- `python3 -m pytest tests/regression tests/cli` passed with 31 tests.
- `python3 -m compileall app` passed.
- Protected file checksum check passed.
- Verification ledger: `.axiom/verification/task_051_verification.json`.

## Self-Audit

- Implemented only roadmap task `051`.
- Did not add persistence writes, provider execution, API endpoints, frontend behavior, or CI behavior.
- Did not edit protected files.
- Did not add dependencies.
- Did not add forbidden infrastructure.
- Added tests for introduced behavior.
- Did not weaken or delete tests.
- Generated machine-readable verification evidence.
