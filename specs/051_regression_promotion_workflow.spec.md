# Spec 051 — Regression Promotion Workflow

## Objective

Create a local workflow to promote failed evaluation samples into reviewable regression suites.

This task must not add persistence writes, provider execution, API endpoints, frontend behavior, or CI behavior.

## Required Behavior

Regression promotion must:

- accept an evaluation run record and matching test cases,
- promote errored samples,
- promote succeeded samples with failed metric metadata,
- deduplicate promoted cases by test case id while preserving first failure order,
- preserve source run id, project id, dataset id, source metadata, test case inputs, expected outputs, and failure reasons,
- reject missing test cases for failed samples,
- reject runs with no promotable failures,
- produce deterministic JSON-compatible output.

CLI behavior must:

- add a `promote-regressions` subcommand,
- require `--run-file`, `--test-cases-file`, `--output-file`, `--suite-id`, and `--suite-name`,
- write reviewable JSON output,
- exit `0` on success and `2` on input errors.

## Verification

Run:

```bash
python3 -m pytest tests/regression tests/cli
python3 -m compileall app
```

## Acceptance Criteria

- [ ] Errored samples promote into regression cases.
- [ ] Metric-failed samples promote into regression cases.
- [ ] Duplicate failed samples are deduplicated by test case id.
- [ ] Source run metadata is preserved in promotion output.
- [ ] Promotion output is deterministic JSON-compatible data.
- [ ] CLI writes reviewable promotion JSON.
- [ ] CLI returns exit code `2` for invalid inputs.
- [ ] Existing regression and CLI tests still pass.
- [ ] Verification evidence exists in `.axiom/verification/task_051_verification.json`.
- [ ] Task report exists in `.axiom/reports/task_051_report.md`.
