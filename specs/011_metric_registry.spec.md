# Spec 011 — Metric Registry

## Objective

Create a typed registry that maps metric specifications to deterministic metric functions.

This task must not add LLM judges, provider calls, persistence, CLI behavior, or external metric libraries.

## Required Structure

```text
app/metrics/
  registry.py

tests/metrics/
  test_metric_registry.py
```

## Required Behavior

Metric specifications must:

- be Pydantic models,
- include `name` and `parameters`,
- reject blank names,
- produce deterministic JSON-compatible dumps.

Registry behavior must:

- support `exact_match`,
- support `regex_match`,
- support `numeric_tolerance`,
- support `json_schema_match`,
- reject unknown metric names,
- reject missing or invalid required parameters,
- evaluate one metric spec or an ordered list of metric specs.

## Verification

Run:

```bash
python3 -m pytest tests/metrics
python3 -m compileall app
```

## Acceptance Criteria

- [ ] Metric spec model exists and validates names.
- [ ] Registry evaluates exact match specs.
- [ ] Registry evaluates regex specs.
- [ ] Registry evaluates numeric tolerance specs.
- [ ] Registry evaluates JSON schema specs.
- [ ] Registry rejects unknown specs and invalid configs.
- [ ] Ordered spec evaluation is deterministic.
- [ ] Verification evidence exists in `.axiom/verification/task_011_verification.json`.
- [ ] Task report exists in `.axiom/reports/task_011_report.md`.
