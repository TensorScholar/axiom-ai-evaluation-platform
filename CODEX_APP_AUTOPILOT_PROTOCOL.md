# AXIOM Codex App Autopilot Protocol v0.5

## Purpose

This protocol is optimized for the Codex macOS app workflow:

```text
Open folder → give one start prompt → Codex loops through task graph → verification ledgers prove progress
```

The user should not need to prompt each step manually.

## Main Loop

For each iteration:

1. Read `.axiom/state/task_status.json`.
2. Select the first task with status `unlocked`.
3. Read the matching spec from `specs/`.
4. Inspect only relevant files.
5. Plan the minimal implementation.
6. Implement only the current task.
7. Add tests required by the spec.
8. Run:

```bash
python scripts/axiom_verify.py --task <TASK_ID>
```

9. If verification fails, repair within task scope.
10. Retry up to 3 repair loops.
11. Generate `.axiom/reports/task_<TASK_ID>_report.md`.
12. Run self-audit checklist.
13. If verification and self-audit pass:
    - mark current task `completed`,
    - unlock the next task,
    - continue automatically.
14. If a stop condition is triggered, stop and report.

## Completion Rule

A task is complete only if all are true:

- implementation matches the spec,
- required tests exist,
- verifier exits with code 0,
- `.axiom/verification/task_<TASK_ID>_verification.json` exists,
- `.axiom/reports/task_<TASK_ID>_report.md` exists,
- protected file checks pass,
- self-audit checklist passes.

## User Interaction Rule

Do not ask the user for routine choices.

Ask only for:

- new production dependency,
- architecture change,
- protected file change,
- security/auth behavior change,
- destructive command,
- unclear acceptance criteria affecting data model, API, persistence, safety, or security.

## Anti-Drift Rule

Do not make product or architecture decisions beyond the current spec.

If the current task is scaffold, do not implement domain model.
If the current task is domain model, do not implement providers.
If the current task is providers, do not implement judge reliability.
