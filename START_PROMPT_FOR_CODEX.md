# Start Prompt for Codex App

Copy this prompt into Codex after opening this folder as the project.

```text
You are operating in AXIOM Codex App Autopilot Mode.

First read these files in order:
1. AGENTS.md
2. CODEX_APP_AUTOPILOT_PROTOCOL.md
3. AUTONOMY_POLICY.md
4. VALIDATION_POLICY.md
5. TASK_GRAPH.yaml
6. .axiom/state/task_status.json
7. STOP_CONDITIONS.md
8. GLOBAL_CONSTRAINTS.md
9. NON_GOALS.md

Your job is to implement AXIOM autonomously inside this folder with minimum user interaction.

Execution rules:
- Start from the first unlocked task in .axiom/state/task_status.json.
- For each task, read its matching spec in specs/.
- Implement only that task.
- Do not implement future tasks early.
- Do not edit protected files.
- Run internal verification:
  python scripts/axiom_verify.py --task <TASK_ID>
- Generate:
  .axiom/verification/task_<TASK_ID>_verification.json
  .axiom/reports/task_<TASK_ID>_report.md
- Run the self-audit checklist in SELF_AUDIT_CHECKLIST.md.
- Update .axiom/state/task_status.json only after verification passes.
- Unlock the next task only after the current task passes.
- Continue automatically to the next unlocked task.

Do not ask me for step-by-step approval.
Ask only if a stop condition is triggered.

A task is not complete unless there is machine-readable verification evidence.
Do not claim validation from text alone.
Do not weaken tests.
Do not delete tests.
Do not modify scripts/axiom_verify.py or protected policy files.
Stop if protected file checksums fail.
```
