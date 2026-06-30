# Spec 007 — Regression Suite Records and Rerun Plans

## Objective

Create deterministic records for converting failures into regression test cases and planning reruns against new model or prompt versions.

This task defines in-memory regression suite records and rerun plans only. It must not execute suites, call providers, persist results, implement CI gates, or import traces.

## Required Structure

```text
app/regression/
  __init__.py
  models.py
  suite.py

tests/regression/
  test_regression_suite.py
```

## Required Behavior

Regression case records must:

- be Pydantic models,
- include `id`, `source_run_id`, `test_case`, and `failure_reason`,
- reject blank ids and failure reasons,
- produce deterministic JSON-compatible dumps.

Regression suite records must:

- be Pydantic models,
- include `id`, `name`, and `cases`,
- reject blank ids and names,
- reject empty case lists,
- reject duplicate case ids.

Rerun plan records must:

- be Pydantic models,
- include `suite_id`, `model_name`, `prompt_version`, and ordered `case_ids`,
- reject blank model names and prompt versions,
- preserve case order deterministically.

Required helpers:

- `failure_to_regression_case(...) -> RegressionCase`
- `build_regression_suite(...) -> RegressionSuite`
- `plan_regression_rerun(suite, model_name, prompt_version) -> RegressionRerunPlan`

## Forbidden

Do not implement:

- suite execution,
- provider API calls,
- evaluation engine integration,
- CI gate behavior,
- persistence,
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
python scripts/axiom_verify.py --task 007
```

## Acceptance Criteria

- [ ] Regression case records exist and validate required fields.
- [ ] Failures can be converted into regression cases.
- [ ] Regression suite records validate non-empty unique case ids.
- [ ] Rerun plans preserve deterministic case order.
- [ ] `tests/regression` coverage exists for introduced behavior.
- [ ] `python scripts/axiom_verify.py --task 007` passes.
- [ ] `.axiom/verification/task_007_verification.json` exists.
- [ ] `.axiom/reports/task_007_report.md` exists.
- [ ] no forbidden infrastructure is introduced.
- [ ] no future milestone is implemented early.
