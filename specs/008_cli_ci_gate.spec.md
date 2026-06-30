# Spec 008 — CLI CI Regression Gate

## Objective

Create a minimal CLI command that exits nonzero when a precomputed regression gate result fails.

This task defines CI gate result validation and exit-code behavior only. It must not execute evaluations, call providers, persist data, create package entry points, or implement trace import.

## Required Structure

```text
app/
  ci_gate.py
  cli.py

tests/cli/
  test_ci_gate.py
```

## Required Behavior

Gate failure records must:

- be Pydantic models,
- include `case_id` and `reason`,
- reject blank fields,
- produce deterministic JSON-compatible dumps.

Gate result records must:

- be Pydantic models,
- include `suite_id`, `passed`, `failures`, and `metrics`,
- reject blank suite ids,
- allow JSON-compatible metric values,
- produce deterministic JSON-compatible dumps.

Gate decision behavior must:

- return `0` when `passed` is true and there are no failures,
- return `1` when `passed` is false or failures are present.

CLI behavior must:

- expose `main(argv=None) -> int`,
- support `gate --result-file <path>`,
- read a JSON gate result file,
- print `AXIOM gate passed: <suite_id>` on success,
- print `AXIOM gate failed: <suite_id>` on gate failure,
- print clear errors and return `2` for missing files, invalid JSON, or invalid gate result structure.

## Forbidden

Do not implement:

- evaluation execution,
- provider API calls,
- regression suite execution,
- packaging entry points,
- persistence,
- frontend,
- trace import,
- Kafka,
- Kubernetes,
- Celery,
- Qdrant,
- event sourcing,
- microservices.

## Verification

Run:

```bash
python scripts/axiom_verify.py --task 008
```

## Acceptance Criteria

- [ ] Gate failure and result records exist and validate required fields.
- [ ] Gate decision returns `0` for pass and `1` for failed gates.
- [ ] CLI returns `0` for passing result files.
- [ ] CLI returns `1` for failing result files.
- [ ] CLI returns `2` for input/validation errors.
- [ ] `tests/cli` coverage exists for introduced behavior.
- [ ] `python scripts/axiom_verify.py --task 008` passes.
- [ ] `.axiom/verification/task_008_verification.json` exists.
- [ ] `.axiom/reports/task_008_report.md` exists.
- [ ] no forbidden infrastructure is introduced.
- [ ] no future milestone is implemented early.
