# Spec 040 - OpenAI Provider Adapter

## Objective

Add a real OpenAI provider adapter behind the existing provider protocol.

This task must not read secrets implicitly, make network calls in tests, add async streaming, add retries, or change the provider protocol.

## Required Behavior

OpenAI provider adapter must:

- require an explicitly supplied OpenAI-compatible client,
- call `client.responses.create` with `model` and `input`,
- pass request parameters through as keyword arguments,
- convert the response into `ProviderResponse`,
- extract text from `output_text` when present,
- include response id, model, and usage metadata when available,
- raise a clear error when response text cannot be extracted.

Tests must use a fake client and must not perform network calls.

## Verification

Run:

```bash
python3 -m pytest tests/providers
python3 -m compileall app
```

## Acceptance Criteria

- [ ] OpenAI provider requires explicit client configuration.
- [ ] OpenAI provider calls responses.create with model and input.
- [ ] Request parameters pass through to the SDK call.
- [ ] OpenAI responses convert into ProviderResponse.
- [ ] Missing response text raises a clear error.
- [ ] Tests do not perform network calls.
- [ ] Verification evidence exists in `.axiom/verification/task_040_verification.json`.
- [ ] Task report exists in `.axiom/reports/task_040_report.md`.
