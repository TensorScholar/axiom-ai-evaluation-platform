# Spec 005 — LLM Judge Abstraction and Structured Results

## Objective

Create a minimal LLM-as-judge abstraction with rubric versioning and structured judge results.

This task defines typed judge records and a local scripted judge only. It must not call LLM providers, treat judge output as objective truth, implement judge reliability, aggregate scores, run regression suites, persist data, or expose CLI behavior.

## Required Structure

```text
app/judges/
  __init__.py
  base.py
  models.py
  scripted.py

tests/judges/
  test_judge_layer.py
```

## Required Behavior

Rubric version records must:

- be Pydantic models,
- include `rubric_id`, `version`, and `criteria`,
- reject blank versions,
- reject empty criteria and blank criteria.

Judge requests must:

- be Pydantic models,
- include `test_case_id`, `rubric`, `prompt`, `output`, and optional `expected_output`,
- reject blank prompt and output,
- produce deterministic JSON-compatible dumps.

Judge results must:

- be Pydantic models,
- include `test_case_id`, `rubric_id`, `rubric_version`, `verdict`, `score`, `rationale`, `criteria_scores`, and `metadata`,
- support verdicts `passed` and `failed`,
- require score and criteria scores between `0.0` and `1.0`,
- reject blank rationales and blank criteria-score keys,
- produce deterministic JSON-compatible dumps.

Judge adapter interface must:

- expose a synchronous `judge(request)` method,
- accept a `JudgeRequest`,
- return a `JudgeResult`.

Scripted judge must:

- implement the judge adapter interface,
- return deterministic scripted results in order,
- record every request it receives,
- raise a clear error when no scripted result remains.

## Forbidden

Do not implement:

- real LLM judge provider calls,
- prompt execution,
- judge reliability or calibration,
- score aggregation,
- regression suites,
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
python scripts/axiom_verify.py --task 005
```

## Acceptance Criteria

- [ ] Rubric version records exist and validate required fields.
- [ ] Judge request records exist and validate required fields.
- [ ] Judge result records exist and validate verdict, score, rationale, and criteria scores.
- [ ] Judge adapter interface exists.
- [ ] Scripted judge returns results in order and records requests.
- [ ] `tests/judges` coverage exists for introduced behavior.
- [ ] `python scripts/axiom_verify.py --task 005` passes.
- [ ] `.axiom/verification/task_005_verification.json` exists.
- [ ] `.axiom/reports/task_005_report.md` exists.
- [ ] no forbidden infrastructure is introduced.
- [ ] no future milestone is implemented early.
