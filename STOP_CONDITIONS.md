# AXIOM Stop Conditions v0.5

Codex must stop if:

- verification fails after 3 repair loops,
- protected file checksum fails,
- protected file needs to be changed,
- a fix requires a new dependency,
- a fix requires architecture change,
- a fix requires forbidden infrastructure,
- tests cannot run,
- acceptance criteria are ambiguous and affect API, persistence, safety, or security,
- implementation would require weakening tests,
- implementation would require deleting tests,
- current task cannot be completed without future task work.

When stopping, write:

```text
.axiom/reports/STOP_REPORT.md
```

Include:

- stop condition,
- evidence,
- changed files,
- failed commands,
- safest next action.
