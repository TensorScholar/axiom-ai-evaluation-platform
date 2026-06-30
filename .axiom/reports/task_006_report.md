# Task 006 Report — Judge Reliability Signals

## Summary

Expanded and implemented task `006` as deterministic reliability analysis for existing structured judge results.

## Spec Update

The previously incomplete task `006` spec was replaced under explicit user approval with concrete structure, behavior, forbidden scope, verification, and acceptance criteria.

## Changes

- Added `JudgeReliabilityReport` Pydantic model.
- Added `position_swap_consistent`.
- Added `assess_judge_reliability`.
- Added focused tests in `tests/judges/test_judge_reliability.py`.

## Validation

- `python3 -m pytest tests/judges` passed with 20 tests.
- `python3 -m compileall app` passed.
- `python3 scripts/axiom_verify.py --task 006` is the task verifier command used in this environment because `python` is not available on PATH.
- Verification ledger: `.axiom/verification/task_006_verification.json`.
- Verifier overall status: `passed`.
- Protected file checksum check: `passed`.

## Self-Audit

- Implemented only task `006`.
- Did not implement future task behavior.
- Satisfied all task `006` acceptance criteria.
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
- Did not add real LLM judge provider calls, prompt execution, calibration datasets, judge training, regression aggregation, persistence, CLI, frontend, or trace import.
