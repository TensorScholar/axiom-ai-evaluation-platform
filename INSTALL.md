# AXIOM Local Installation

Install AXIOM from this repository for local CLI usage:

```bash
python3 -m pip install -e .
```

After installation, the stable console command is:

```bash
axiom --help
```

The package exposes the existing local commands:

- `eval`
- `gate`
- `summarize-gate`
- `trace-import`
- `promote-regressions`

No external provider credentials are required for fake-provider evaluation, trace import, regression promotion, gate checks, or packaging validation.
