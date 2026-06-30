# Spec 003 — Provider Adapter Interface and Fake Provider

## Objective

Create a typed provider adapter boundary and deterministic fake provider for tests before real API integration.

This task defines request/response models and a local fake implementation only. It must not integrate with external model APIs, secrets, auth, retries, streaming, async workers, persistence, metrics, judges, or CLI behavior.

## Required Structure

```text
app/providers/
  __init__.py
  base.py
  fake.py
  models.py

tests/providers/
  test_fake_provider.py
```

## Required Behavior

Provider requests must:

- be Pydantic models,
- include `prompt`, `model_name`, and `parameters`,
- reject blank prompt and model name,
- allow JSON-compatible parameter values,
- produce deterministic JSON-compatible dumps.

Provider responses must:

- be Pydantic models,
- include `text`, `model_name`, and `metadata`,
- reject blank text and model name,
- allow JSON-compatible metadata values,
- produce deterministic JSON-compatible dumps.

Provider adapter interface must:

- expose a synchronous `generate(request)` method,
- accept a `ProviderRequest`,
- return a `ProviderResponse`.

Fake provider must:

- implement the provider adapter interface,
- return deterministic scripted responses in order,
- optionally fall back to echoing the request prompt when no scripted responses remain,
- record every request it receives,
- raise a clear error when no scripted responses remain and echo fallback is disabled.

## Forbidden

Do not implement:

- real provider API integration,
- network calls,
- credentials or auth,
- retries or rate limiting,
- streaming,
- async execution,
- database models,
- repositories,
- evaluation execution,
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
python scripts/axiom_verify.py --task 003
```

## Acceptance Criteria

- [ ] Provider request and response models exist and validate required fields.
- [ ] Provider adapter interface exists.
- [ ] Fake provider implements deterministic scripted responses.
- [ ] Fake provider records requests.
- [ ] Fake provider echo fallback is deterministic and configurable.
- [ ] `tests/providers` coverage exists for introduced behavior.
- [ ] `python scripts/axiom_verify.py --task 003` passes.
- [ ] `.axiom/verification/task_003_verification.json` exists.
- [ ] `.axiom/reports/task_003_report.md` exists.
- [ ] no forbidden infrastructure is introduced.
- [ ] no future milestone is implemented early.
