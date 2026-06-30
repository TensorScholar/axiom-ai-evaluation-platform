# AXIOM Autonomy Policy v0.5

## Goal

Minimize the user's involvement while keeping Codex bounded by objective verification and explicit constraints.

## Allowed Autonomy

Codex may:

- choose the next unlocked task,
- decide local implementation details,
- create tests,
- run commands,
- repair failures,
- update task status after verified success,
- continue to the next unlocked task.

## Forbidden Autonomy

Codex may not:

- change goals,
- change architecture,
- edit protected files,
- change task order,
- change acceptance criteria,
- add forbidden technologies,
- add dependencies without approval,
- treat its own explanation as validation.

## Autonomy Level

This pack uses:

```text
Level 3.75 — Codex-app internal autopilot with evidence-gated progress
```

It is more automatic than manual prompting, but less secure than an external verifier.
