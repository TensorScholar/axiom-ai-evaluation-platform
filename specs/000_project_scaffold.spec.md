# Spec 000 — Project Scaffold

## Objective

Create the initial AXIOM project scaffold as a minimal, testable Python application.

This task must create only the foundation needed for future specs. It must not implement evaluation logic yet.

## Required Structure

```text
app/
  __init__.py
  main.py
  config.py
  domain/__init__.py
  evaluations/__init__.py
  providers/__init__.py
  metrics/__init__.py
  judges/__init__.py
  regression/__init__.py
  traces/__init__.py

tests/
  test_app_import.py
  test_health.py
```

If using FastAPI, `app/main.py` must expose an `app` object.

## Required Behavior

`GET /health` returns:

```json
{
  "status": "ok",
  "service": "axiom"
}
```

## Allowed Dependencies

Use minimum dependencies only.

Preferred:

- fastapi
- pydantic
- pytest

## Forbidden

Do not implement:

- database models,
- provider adapters,
- evaluation runs,
- metrics,
- judges,
- regression suites,
- CLI,
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
python scripts/axiom_verify.py --task 000
```

## Acceptance Criteria

- [ ] `app` package exists.
- [ ] app imports successfully.
- [ ] health endpoint exists.
- [ ] health endpoint returns service status.
- [ ] tests pass.
- [ ] verification ledger exists.
- [ ] task report exists.
- [ ] no forbidden infrastructure is introduced.
- [ ] no future milestone is implemented early.
