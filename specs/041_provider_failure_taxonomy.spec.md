# Spec 041 — Provider Failure Taxonomy

## Objective

Normalize provider failures into typed error categories and preserve them in sample-level error records.

This task must not add retry logic, network behavior, provider execution changes, persistence, or CLI behavior.

## Required Behavior

Provider failure taxonomy must:

- define categories `validation`, `auth`, `rate_limit`, `timeout`, and `unknown`,
- expose a Pydantic `ProviderFailure` model,
- reject blank provider names and messages,
- normalize common exception class names and messages into categories,
- produce deterministic JSON-compatible dumps.

Evaluation runner behavior must:

- convert provider exceptions into normalized provider failure metadata,
- keep existing sample error behavior,
- preserve exception type metadata.

## Verification

Run:

```bash
python3 -m pytest tests/providers tests/evaluations
python3 -m compileall app
```

## Acceptance Criteria

- [ ] Provider failure model validates fields.
- [ ] Auth, rate-limit, timeout, validation, and unknown failures are classified.
- [ ] Runner records provider failure metadata on errored samples.
- [ ] Existing provider and evaluation tests still pass.
- [ ] Verification evidence exists in `.axiom/verification/task_041_verification.json`.
- [ ] Task report exists in `.axiom/reports/task_041_report.md`.
