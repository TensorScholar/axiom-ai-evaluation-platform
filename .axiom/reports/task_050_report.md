# Task 050 Report — Trace File Import CLI

## Summary

Added a local `trace-import` CLI path that imports trace batch JSON files, selects failed traces, and writes converted test cases or regression cases.

## Changes

- Added `specs/050_trace_file_import_cli.spec.md`.
- Added `app.trace_file_import` for local trace-file import and deterministic output writing.
- Added `trace-import` CLI subcommand with `test-cases` and `regression-cases` output modes.
- Added trace-file import tests and CLI tests.

## Validation

- `python3 scripts/axiom_verify.py --task 050` returned `Unknown task: 050` because the protected verifier only defines tasks `000` through `009`.
- `python3 -m pytest tests/traces tests/cli` passed with 31 tests.
- `python3 -m compileall app` passed.
- Protected file checksum check passed.
- Verification ledger: `.axiom/verification/task_050_verification.json`.

## Self-Audit

- Implemented only roadmap task `050`.
- Did not add persistence, provider execution, API endpoints, frontend behavior, or regression promotion deduplication.
- Did not edit protected files.
- Did not add dependencies.
- Did not add forbidden infrastructure.
- Added tests for introduced behavior.
- Did not weaken or delete tests.
- Generated machine-readable verification evidence.
