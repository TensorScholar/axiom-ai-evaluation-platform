# Spec 021 — Gate Integration Over Evaluation Summaries

## Objective

Connect evaluation summaries to the existing CI gate result format.

This task must preserve existing `gate --result-file` behavior and must not add evaluation execution, persistence, provider calls, or external CI configuration.

## Required Behavior

Gate conversion must:

- convert an `EvaluationRunSummary` into a `GateResult`,
- pass when `pass_rate >= min_pass_rate` and `error_rate <= max_error_rate`,
- fail with clear failure reasons when thresholds are violated,
- reject thresholds outside `0.0` to `1.0`,
- produce deterministic JSON-compatible dumps.

CLI behavior must:

- support `summarize-gate --summary-file <path> --output-file <path>`,
- accept `--min-pass-rate` and `--max-error-rate`,
- read an evaluation summary JSON file,
- write a gate result JSON file,
- return `0` on valid conversion,
- return `2` on missing files, invalid JSON, invalid summary shape, invalid thresholds, or write errors.

## Verification

Run:

```bash
python3 -m pytest tests/cli
python3 -m compileall app
```

## Acceptance Criteria

- [ ] Evaluation summaries convert to passing gate results.
- [ ] Evaluation summaries convert to failing gate results with reasons.
- [ ] Invalid thresholds are rejected.
- [ ] CLI writes gate result JSON.
- [ ] Existing gate command behavior remains covered.
- [ ] Verification evidence exists in `.axiom/verification/task_021_verification.json`.
- [ ] Task report exists in `.axiom/reports/task_021_report.md`.
