# Spec 020 — Local Eval CLI

## Objective

Add CLI support for running a local evaluation from JSON fixtures using the fake provider and writing a JSON result file.

This task must not add real provider calls, persistence, packaging entry points, external services, or trace import behavior.

## Required Behavior

CLI command:

```bash
axiom eval --dataset-file dataset.json --provider-file provider.json --output-file result.json
```

Dataset fixture must include:

- `run_id`
- `project_id`
- `dataset_id`
- `model_name`
- `metadata`
- `test_cases`

Provider fixture must include:

- `responses`
- optional `echo_fallback`

The command must:

- validate fixture shape,
- run the in-memory evaluation runner,
- write the evaluation run JSON to `output-file`,
- print `AXIOM eval completed: <run_id>`,
- return `0` on success,
- return `2` on missing files, invalid JSON, invalid fixtures, or write errors.

## Verification

Run:

```bash
python3 -m pytest tests/cli
python3 -m compileall app
```

## Acceptance Criteria

- [ ] JSON fixtures are validated.
- [ ] Fake provider scripted responses are loaded.
- [ ] CLI writes deterministic evaluation run JSON.
- [ ] CLI returns `0` on success.
- [ ] CLI returns `2` on input or output errors.
- [ ] Verification evidence exists in `.axiom/verification/task_020_verification.json`.
- [ ] Task report exists in `.axiom/reports/task_020_report.md`.
