# Spec 012 — Evaluation Run Summary

## Objective

Create deterministic summary records over evaluation run sample results.

This task must not add persistence, CLI behavior, provider calls, regression execution, or dashboards.

## Required Structure

```text
app/evaluations/
  summary.py

tests/evaluations/
  test_summary.py
```

## Required Behavior

Evaluation summaries must:

- be Pydantic models,
- include run id, status, total samples, succeeded samples, errored samples, metric count, passed metrics, failed metrics, pass rate, and error rate,
- require count fields to be non-negative,
- require rate fields between `0.0` and `1.0`,
- produce deterministic JSON-compatible dumps.

Summary behavior must:

- summarize `EvaluationRunRecord` sample outcomes,
- read metric result metadata from sample metadata,
- count metric results with `passed: true` and `passed: false`,
- calculate pass rate as passed metrics divided by total metrics,
- calculate error rate as errored samples divided by total samples,
- use `0.0` pass rate when no metric results exist.

## Verification

Run:

```bash
python3 -m pytest tests/evaluations
python3 -m compileall app
```

## Acceptance Criteria

- [ ] Evaluation summary model exists and validates counts/rates.
- [ ] Summary counts succeeded and errored samples.
- [ ] Summary counts passed and failed metric metadata.
- [ ] Summary calculates pass and error rates deterministically.
- [ ] Empty runs produce deterministic zero rates.
- [ ] Verification evidence exists in `.axiom/verification/task_012_verification.json`.
- [ ] Task report exists in `.axiom/reports/task_012_report.md`.
