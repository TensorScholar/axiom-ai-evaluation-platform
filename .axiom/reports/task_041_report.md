# Task 041 Report — Provider Failure Taxonomy

## Summary

Implemented normalized provider failure metadata for provider exceptions captured by the evaluation runner.

## Changes

- Added `specs/041_provider_failure_taxonomy.spec.md`.
- Added `ProviderFailureCategory`, `ProviderFailure`, and `classify_provider_exception`.
- Exported provider failure APIs from `app.providers`.
- Updated evaluation runner error handling to preserve provider failure metadata while keeping existing sample error behavior.
- Added provider taxonomy tests and updated runner tests for errored sample metadata.

## Validation

- `python3 scripts/axiom_verify.py --task 041` returned `Unknown task: 041` because the protected verifier only defines tasks `000` through `009`.
- `python3 -m pytest tests/providers tests/evaluations` passed with 37 tests.
- `python3 -m compileall app` passed.
- Protected file checksum check passed.
- Verification ledger: `.axiom/verification/task_041_verification.json`.

## Self-Audit

- Implemented only roadmap task `041`.
- Did not implement retry logic, network behavior changes, persistence, or CLI behavior.
- Did not edit protected files.
- Did not add dependencies.
- Did not add forbidden infrastructure.
- Added tests for introduced behavior.
- Did not weaken or delete tests.
- Generated machine-readable verification evidence.
