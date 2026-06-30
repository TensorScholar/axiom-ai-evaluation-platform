# Spec 001 — Core Domain Model

## Objective

Create minimal, typed domain models for AXIOM projects, datasets, test cases, rubrics, and evaluation run identifiers.

This task defines in-memory validation objects only. It must not implement persistence, evaluation execution, provider adapters, metrics, judges, regression suites, CLI behavior, or trace import.

## Required Structure

```text
app/domain/
  __init__.py
  identifiers.py
  models.py

tests/domain/
  test_core_models.py
```

## Required Behavior

Domain identifiers must:

- be explicit string value objects,
- reject empty or whitespace-only values,
- preserve valid values exactly,
- expose stable string conversion with `str(identifier)`.

Required identifiers:

- `ProjectId`
- `DatasetId`
- `TestCaseId`
- `RubricId`
- `EvaluationRunId`

Domain models must:

- be Pydantic models,
- validate required identifiers,
- reject empty required text fields,
- reject empty test case input dictionaries,
- expose deterministic model dumps.

Required models:

- `Project`
  - `id: ProjectId`
  - `name: str`
- `Dataset`
  - `id: DatasetId`
  - `project_id: ProjectId`
  - `name: str`
- `TestCase`
  - `id: TestCaseId`
  - `dataset_id: DatasetId`
  - `name: str`
  - `inputs: dict[str, object]`
  - `expected_output: str | None = None`
- `Rubric`
  - `id: RubricId`
  - `project_id: ProjectId`
  - `name: str`
  - `criteria: list[str]`
- `EvaluationRunReference`
  - `id: EvaluationRunId`
  - `project_id: ProjectId`
  - `dataset_id: DatasetId`

Rubrics must reject an empty criteria list and whitespace-only criteria.

## Forbidden

Do not implement:

- database models,
- repositories,
- evaluation run execution,
- provider adapters,
- metrics,
- judges,
- regression suites,
- CLI,
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
python scripts/axiom_verify.py --task 001
```

## Acceptance Criteria

- [ ] Domain identifier classes exist and validate values.
- [ ] Domain models exist and validate required fields.
- [ ] Invalid identifiers, blank names, empty inputs, and empty rubric criteria are rejected.
- [ ] Model dumps are deterministic and JSON-compatible.
- [ ] `tests/domain` coverage exists for introduced behavior.
- [ ] `python scripts/axiom_verify.py --task 001` passes.
- [ ] `.axiom/verification/task_001_verification.json` exists.
- [ ] `.axiom/reports/task_001_report.md` exists.
- [ ] no forbidden infrastructure is introduced.
- [ ] no future milestone is implemented early.
