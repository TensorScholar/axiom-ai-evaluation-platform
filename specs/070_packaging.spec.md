# Spec 070 — Packaging

## Objective

Add minimal Python packaging metadata and local installation documentation for AXIOM.

This task must not publish a package, add deployment automation, add CI, add new runtime behavior, or install dependencies.

## Required Behavior

Packaging must:

- define installable Python package metadata in `pyproject.toml`,
- use the existing `app` package,
- define the project name `axiom-ai-evaluation-platform`,
- define a stable `axiom` console command pointing to the existing CLI entry point,
- declare only existing runtime dependencies,
- document local editable installation,
- document the stable console command.

## Verification

Run:

```bash
python3 -m pytest tests/packaging
python3 -m compileall app
```

## Acceptance Criteria

- [ ] `pyproject.toml` exists with build-system metadata.
- [ ] Project metadata defines name, version, description, readme, Python requirement, and existing dependencies.
- [ ] Package discovery includes the existing `app` package.
- [ ] Console script `axiom` points to `app.cli:main`.
- [ ] Local installation documentation exists.
- [ ] Packaging tests validate metadata and documentation.
- [ ] Verification evidence exists in `.axiom/verification/task_070_verification.json`.
- [ ] Task report exists in `.axiom/reports/task_070_report.md`.
