# Spec 031 — Run History Queries

## Objective

Add query helpers for recent evaluation runs, failed samples, and regression candidates over local SQLite persistence.

This task must not add migrations, web APIs, provider calls, auth, deployment, or external services.

## Required Behavior

Run queries must:

- filter evaluation runs by optional `project_id`, `dataset_id`, and `status`,
- return runs ordered by run id for deterministic local behavior,
- preserve the existing `list_evaluation_runs()` API.

Failed sample queries must:

- return typed failed sample records,
- include run id, test case id, outcome, output, error message, and reason,
- treat errored samples as failures,
- treat samples with failed metric metadata as failures,
- support the same optional run filters.

Regression candidate queries must:

- return typed regression candidate records,
- include run id, test case id, and failure reason,
- be derived from failed sample records deterministically.

## Verification

Run:

```bash
python3 -m pytest tests/persistence
python3 -m compileall app
```

## Acceptance Criteria

- [ ] Evaluation runs can be filtered by project, dataset, and status.
- [ ] Failed samples include errored samples.
- [ ] Failed samples include failed metric samples.
- [ ] Regression candidates are derived from failed samples.
- [ ] Empty query results are handled deterministically.
- [ ] Verification evidence exists in `.axiom/verification/task_031_verification.json`.
- [ ] Task report exists in `.axiom/reports/task_031_report.md`.
