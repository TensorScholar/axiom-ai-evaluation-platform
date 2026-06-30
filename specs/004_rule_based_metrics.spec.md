# Spec 004 — Deterministic Rule-Based Metrics

## Objective

Create deterministic rule-based metrics for exact match, regex match, JSON-schema-style validation, and numeric tolerance.

This task defines local metric helpers only. It must not implement LLM judges, provider calls, regression suites, persistence, CLI behavior, or full JSON Schema compliance.

## Required Structure

```text
app/metrics/
  __init__.py
  deterministic.py
  models.py

tests/metrics/
  test_deterministic_metrics.py
```

## Required Behavior

Metric results must:

- be Pydantic models,
- include `name`, `passed`, `score`, and `details`,
- reject blank names,
- require scores between `0.0` and `1.0`,
- produce deterministic JSON-compatible dumps.

Exact match metric must:

- compare actual and expected values deterministically,
- return a passing score of `1.0` only when values match exactly,
- return a failing score of `0.0` when values differ.

Regex match metric must:

- accept string actual values and regex patterns,
- use `re.search`,
- reject invalid regex patterns with a clear error.

Numeric tolerance metric must:

- accept numeric actual, expected, and tolerance values,
- reject negative tolerance values,
- pass when `abs(actual - expected) <= tolerance`.

JSON schema validation metric must:

- validate JSON-compatible values against a small deterministic schema subset,
- support `type`, `required`, `properties`, `items`, `enum`, and `const`,
- return validation errors in result details,
- avoid adding a JSON Schema dependency.

Supported schema types:

- `object`
- `array`
- `string`
- `number`
- `integer`
- `boolean`
- `null`

## Forbidden

Do not implement:

- LLM judges,
- provider API calls,
- regression suites,
- persistence,
- CLI,
- frontend,
- trace import,
- external JSON Schema libraries,
- Kafka,
- Kubernetes,
- Celery,
- Qdrant,
- event sourcing,
- microservices.

## Verification

Run:

```bash
python scripts/axiom_verify.py --task 004
```

## Acceptance Criteria

- [ ] Metric result model exists and validates name and score.
- [ ] Exact match metric passes and fails deterministically.
- [ ] Regex match metric passes, fails, and rejects invalid patterns.
- [ ] Numeric tolerance metric passes, fails, and rejects negative tolerance.
- [ ] JSON schema validation metric supports the required subset.
- [ ] `tests/metrics` coverage exists for introduced behavior.
- [ ] `python scripts/axiom_verify.py --task 004` passes.
- [ ] `.axiom/verification/task_004_verification.json` exists.
- [ ] `.axiom/reports/task_004_report.md` exists.
- [ ] no forbidden infrastructure is introduced.
- [ ] no future milestone is implemented early.
