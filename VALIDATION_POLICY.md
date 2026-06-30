# AXIOM Validation Policy v0.5

## Core Principle

Validation must be evidence-based.

```text
No JSON ledger = no validation.
No command output = no validation.
No passing exit code = no completion.
No self-audit = no completion.
```

## Required Verification Ledger

Each task must generate:

```text
.axiom/verification/task_<TASK_ID>_verification.json
```

## Required Report

Each task must generate:

```text
.axiom/reports/task_<TASK_ID>_report.md
```

## Fake Validation Prohibited

Codex must not:

- say tests passed without running them,
- omit failing output,
- delete tests,
- weaken tests,
- change verifier to pass,
- mark complete without ledger,
- mark complete without report,
- claim manual validation without evidence.

## Protected Files

Do not modify:

```text
AGENTS.md
CODEX_APP_AUTOPILOT_PROTOCOL.md
AUTONOMY_POLICY.md
VALIDATION_POLICY.md
STOP_CONDITIONS.md
GLOBAL_CONSTRAINTS.md
NON_GOALS.md
TASK_GRAPH.yaml
scripts/axiom_verify.py
PROTECTED_FILE_MANIFEST.json
SELF_AUDIT_CHECKLIST.md
```

If a protected file must change, stop and ask.
