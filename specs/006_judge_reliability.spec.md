# Spec 006 — Judge Reliability Signals

## Objective

Create deterministic judge reliability signals for position-swap consistency, multi-judge agreement, confidence, uncertainty, and human-review flags.

This task analyzes already-structured judge results only. It must not call LLM providers, execute judges, perform calibration, aggregate regression suites, persist data, or expose CLI behavior.

## Required Structure

```text
app/judges/
  reliability.py

tests/judges/
  test_judge_reliability.py
```

## Required Behavior

Reliability reports must:

- be Pydantic models,
- include judge count, majority verdict, agreement rate, mean score, score spread, confidence, uncertainty, optional position-swap consistency, human-review flag, and review reasons,
- require rate-like fields between `0.0` and `1.0`,
- reject blank review reasons,
- produce deterministic JSON-compatible dumps.

Position-swap consistency must:

- compare two `JudgeResult` records,
- pass only when verdicts match and score delta is within tolerance,
- reject negative tolerances.

Multi-judge reliability assessment must:

- reject empty result lists,
- calculate majority verdict,
- calculate agreement rate,
- calculate mean score and score spread,
- calculate confidence as agreement adjusted by score spread,
- calculate uncertainty as `1.0 - confidence`,
- flag human review when confidence is below threshold,
- flag human review when no majority verdict exists,
- flag human review when position-swap consistency fails.

Required helpers:

- `position_swap_consistent(original, swapped, score_tolerance=0.15) -> bool`
- `assess_judge_reliability(results, swapped_result=None, score_tolerance=0.15, confidence_threshold=0.75) -> JudgeReliabilityReport`

## Forbidden

Do not implement:

- real LLM judge provider calls,
- prompt execution,
- calibration datasets,
- judge training,
- score aggregation across regression suites,
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
python scripts/axiom_verify.py --task 006
```

## Acceptance Criteria

- [ ] Reliability report model exists and validates required fields.
- [ ] Position-swap consistency passes and fails deterministically.
- [ ] Empty judge result lists are rejected.
- [ ] Multi-judge agreement and majority verdict are calculated.
- [ ] Confidence, uncertainty, and human-review flags are calculated.
- [ ] `tests/judges` coverage exists for introduced behavior.
- [ ] `python scripts/axiom_verify.py --task 006` passes.
- [ ] `.axiom/verification/task_006_verification.json` exists.
- [ ] `.axiom/reports/task_006_report.md` exists.
- [ ] no forbidden infrastructure is introduced.
- [ ] no future milestone is implemented early.
