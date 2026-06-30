# Spec 010 — In-Memory Evaluation Runner

## Objective

Create a synchronous in-memory evaluation runner that executes domain test cases through a provider adapter and records sample-level results with deterministic metric metadata.

This task must not add persistence, real provider integrations, async workers, regression execution, trace import, or frontend behavior.

## Required Structure

```text
app/evaluations/
  runner.py

tests/evaluations/
  test_runner.py
```

## Required Behavior

The runner must:

- accept a non-empty list of `TestCase` records,
- create an `EvaluationRunRecord`,
- transition the run from `pending` to `running` to `completed`,
- call a `ProviderAdapter` once per test case,
- build deterministic prompts from test case inputs,
- record successful provider responses as `SampleResult` records,
- record provider exceptions as errored `SampleResult` records,
- include provider metadata in sample metadata,
- apply exact-match metric metadata when `expected_output` exists,
- avoid mutating the previous run records.

Prompt building must:

- use `inputs["prompt"]` when it is a string,
- otherwise use deterministic JSON with sorted keys.

## Forbidden

Do not implement:

- real provider API calls,
- persistence,
- async execution,
- retry logic,
- regression execution,
- CLI integration,
- trace import,
- frontend,
- Kafka,
- Kubernetes,
- Celery,
- Qdrant,
- event sourcing,
- microservices.

## Verification

Run:

```bash
python3 -m pytest tests/evaluations
python3 -m compileall app
```

## Acceptance Criteria

- [ ] Non-empty test case validation exists.
- [ ] Deterministic prompt building exists.
- [ ] Successful provider responses produce successful sample records.
- [ ] Provider exceptions produce errored sample records.
- [ ] Exact-match metric metadata is recorded when expected output exists.
- [ ] Run status transitions end in `completed`.
- [ ] Tests cover introduced behavior.
- [ ] Verification evidence exists in `.axiom/verification/task_010_verification.json`.
- [ ] Task report exists in `.axiom/reports/task_010_report.md`.
