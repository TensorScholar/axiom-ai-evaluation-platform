# Spec 050 — Trace File Import CLI

## Objective

Expose existing trace import behavior through a local JSON-file CLI command.

This task must not add persistence, provider execution, regression promotion deduplication, API endpoints, or frontend behavior.

## Required Behavior

Trace file import must:

- read a local JSON trace batch file,
- validate it through the existing trace import model,
- select failed traces deterministically,
- convert failed traces into test cases,
- optionally convert failed traces into regression cases when a source run id is provided,
- write deterministic JSON output with import counts and converted items,
- return clear input errors for invalid JSON, invalid trace payloads, missing dataset ids, or missing source run ids for regression output.

CLI behavior must:

- add a `trace-import` subcommand,
- require `--trace-file`, `--output-file`, and `--dataset-id`,
- support `--output-kind test-cases` and `--output-kind regression-cases`,
- require `--source-run-id` for regression case output,
- exit `0` on success and `2` on input errors.

## Verification

Run:

```bash
python3 -m pytest tests/traces tests/cli
python3 -m compileall app
```

## Acceptance Criteria

- [ ] Trace batches can be imported from local JSON files.
- [ ] Failed traces are selected and converted into deterministic test case JSON.
- [ ] Failed traces can be converted into deterministic regression case JSON.
- [ ] CLI writes output files and returns clear success text.
- [ ] CLI returns exit code `2` for invalid trace input.
- [ ] Existing trace and CLI tests still pass.
- [ ] Verification evidence exists in `.axiom/verification/task_050_verification.json`.
- [ ] Task report exists in `.axiom/reports/task_050_report.md`.
