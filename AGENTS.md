# AGENTS.md

## Mission

Build AXIOM as a modular, non-overengineered evaluation and regression platform for loop-based AI systems, coding agents, and LLM applications.

AXIOM should turn specs, traces, and failures into executable evaluations that can block regressions before deployment.

## Operating Mode

You are running inside the Codex macOS app.

The user wants minimum interaction. Therefore, operate autonomously after the initial prompt.

Use the task graph and state file to decide what to do next.

## Required Reading

Before implementation, read:

1. `CODEX_APP_AUTOPILOT_PROTOCOL.md`
2. `AUTONOMY_POLICY.md`
3. `VALIDATION_POLICY.md`
4. `TASK_GRAPH.yaml`
5. `.axiom/state/task_status.json`
6. current task spec in `specs/`
7. `GLOBAL_CONSTRAINTS.md`
8. `STOP_CONDITIONS.md`
9. `SELF_AUDIT_CHECKLIST.md`

## Always

- Work on only one unlocked task at a time.
- Implement the smallest useful solution.
- Add or update tests for introduced behavior.
- Run `python scripts/axiom_verify.py --task <TASK_ID>`.
- Generate a verification ledger.
- Generate a task report.
- Run self-audit before marking complete.
- Update task status only after verification passes.
- Continue to the next unlocked task automatically.
- Stop only on stop conditions or approval-required changes.

## Never

- Do not edit protected files.
- Do not change task graph semantics.
- Do not change acceptance criteria.
- Do not add Kafka, Kubernetes, Terraform, Helm, service mesh, event sourcing, or microservices.
- Do not implement future specs early.
- Do not refactor unrelated files.
- Do not weaken tests.
- Do not delete tests.
- Do not fake validation.
- Do not claim completion without JSON ledger evidence.
