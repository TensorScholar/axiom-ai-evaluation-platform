# Spec 071 — CI Workflow

## Objective

Add a minimal GitHub Actions workflow that verifies AXIOM with tests and compile checks.

This task must not add deployment, external service credentials, container builds, Terraform, Kubernetes, Helm, or production release automation.

## Required Behavior

CI workflow must:

- run on pushes to `main`,
- run on pull requests,
- use Python 3.12,
- install the local package and test tools,
- run `python -m pytest`,
- run `python -m compileall app`,
- avoid deployment and external provider/service dependencies.

## Verification

Run:

```bash
python3 -m pytest tests/ci
python3 -m compileall app
```

## Acceptance Criteria

- [ ] GitHub Actions workflow exists under `.github/workflows/`.
- [ ] Workflow runs on pushes to `main` and pull requests.
- [ ] Workflow sets up Python 3.12.
- [ ] Workflow installs the local package and test tools.
- [ ] Workflow runs the test suite.
- [ ] Workflow runs the compile check.
- [ ] Workflow avoids deployment and external service steps.
- [ ] Verification evidence exists in `.axiom/verification/task_071_verification.json`.
- [ ] Task report exists in `.axiom/reports/task_071_report.md`.
