# AXIOM Self-Audit Checklist v0.5

Before marking a task completed, Codex must check:

## Spec Compliance

- [ ] I implemented only the current task.
- [ ] I did not implement future tasks early.
- [ ] I satisfied every acceptance criterion in the task spec.
- [ ] I did not change acceptance criteria.

## Test Integrity

- [ ] I added/updated tests for introduced behavior.
- [ ] I did not weaken tests.
- [ ] I did not delete tests to pass.
- [ ] I ran the required verifier command.

## Validation Evidence

- [ ] JSON verification ledger exists.
- [ ] Task report exists.
- [ ] Verifier exit code is 0.
- [ ] Command output is recorded.

## Constraint Compliance

- [ ] I did not edit protected files.
- [ ] I did not add forbidden infrastructure.
- [ ] I did not add dependencies without approval.
- [ ] I did not refactor unrelated files.

## Decision

If any checkbox fails, do not mark task completed.
