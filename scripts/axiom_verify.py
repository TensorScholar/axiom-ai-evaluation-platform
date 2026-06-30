#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VERIFICATION_DIR = ROOT / ".axiom" / "verification"

TASK_COMMANDS = {
    "000": [[sys.executable, "-m", "pytest"], [sys.executable, "-m", "compileall", "app"]],
    "001": [[sys.executable, "-m", "pytest", "tests/domain"], [sys.executable, "-m", "compileall", "app"]],
    "002": [[sys.executable, "-m", "pytest", "tests/evaluations"], [sys.executable, "-m", "compileall", "app"]],
    "003": [[sys.executable, "-m", "pytest", "tests/providers"], [sys.executable, "-m", "compileall", "app"]],
    "004": [[sys.executable, "-m", "pytest", "tests/metrics"], [sys.executable, "-m", "compileall", "app"]],
    "005": [[sys.executable, "-m", "pytest", "tests/judges"], [sys.executable, "-m", "compileall", "app"]],
    "006": [[sys.executable, "-m", "pytest", "tests/judges"], [sys.executable, "-m", "compileall", "app"]],
    "007": [[sys.executable, "-m", "pytest", "tests/regression"], [sys.executable, "-m", "compileall", "app"]],
    "008": [[sys.executable, "-m", "pytest", "tests/cli"], [sys.executable, "-m", "compileall", "app"]],
    "009": [[sys.executable, "-m", "pytest", "tests/traces"], [sys.executable, "-m", "compileall", "app"]],
}

PROTECTED_FILES = {
    "AGENTS.md",
    "CODEX_APP_AUTOPILOT_PROTOCOL.md",
    "AUTONOMY_POLICY.md",
    "VALIDATION_POLICY.md",
    "STOP_CONDITIONS.md",
    "GLOBAL_CONSTRAINTS.md",
    "NON_GOALS.md",
    "TASK_GRAPH.yaml",
    "scripts/axiom_verify.py",
    "PROTECTED_FILE_MANIFEST.json",
    "SELF_AUDIT_CHECKLIST.md",
}

FORBIDDEN_PATH_PREFIXES = ("infrastructure/", "kubernetes/", "terraform/", "helm/")


def run(cmd: list[str]) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {
        "command": " ".join(cmd),
        "exit_code": proc.returncode,
        "passed": proc.returncode == 0,
        "stdout_excerpt": proc.stdout[-4000:],
        "stderr_excerpt": proc.stderr[-4000:],
    }


def git_output(args: list[str]) -> str | None:
    try:
        proc = subprocess.run(["git", *args], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 0:
            return None
        return proc.stdout.strip()
    except FileNotFoundError:
        return None


def changed_files() -> list[str]:
    out = git_output(["status", "--porcelain"])
    if out is None:
        return []
    files: list[str] = []
    for line in out.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ")[-1].strip()
        files.append(path)
    return sorted(set(files))


def load_manifest() -> dict[str, str]:
    path = ROOT / "PROTECTED_FILE_MANIFEST.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("protected_files", {})
    except Exception:
        return {}


def sha256(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_constraints(files: list[str]) -> list[dict[str, str]]:
    checks = []

    protected_changed = sorted(set(files).intersection(PROTECTED_FILES))
    checks.append({
        "constraint": "protected files not modified in git diff",
        "status": "failed" if protected_changed else "passed",
        "evidence": ", ".join(protected_changed) if protected_changed else "No protected files appear modified."
    })

    infra = [p for p in files if p.startswith(FORBIDDEN_PATH_PREFIXES)]
    checks.append({
        "constraint": "forbidden infrastructure paths untouched",
        "status": "failed" if infra else "passed",
        "evidence": ", ".join(infra) if infra else "No forbidden infrastructure paths changed."
    })

    manifest = load_manifest()
    checksum_failures = []
    for rel, expected in manifest.items():
        p = ROOT / rel
        if not p.exists():
            checksum_failures.append(f"missing:{rel}")
            continue
        if sha256(p) != expected:
            checksum_failures.append(f"changed:{rel}")

    checks.append({
        "constraint": "protected file checksums match manifest",
        "status": "failed" if checksum_failures else "passed",
        "evidence": ", ".join(checksum_failures) if checksum_failures else "Protected file checksums match."
    })

    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    args = parser.parse_args()
    task = args.task

    if task not in TASK_COMMANDS:
        print(f"Unknown task: {task}", file=sys.stderr)
        return 2

    VERIFICATION_DIR.mkdir(parents=True, exist_ok=True)
    commands = [run(cmd) for cmd in TASK_COMMANDS[task]]
    files = changed_files()
    constraints = check_constraints(files)

    report_path = ROOT / ".axiom" / "reports" / f"task_{task}_report.md"
    report_exists = report_path.exists()

    command_pass = all(c["passed"] for c in commands)
    constraint_pass = all(c["status"] == "passed" for c in constraints)
    report_pass = report_exists

    acceptance = [
        {
            "criterion": "required verification commands pass",
            "status": "passed" if command_pass else "failed",
            "evidence": "All command exit codes are 0." if command_pass else "At least one command failed."
        },
        {
            "criterion": "constraint checks pass",
            "status": "passed" if constraint_pass else "failed",
            "evidence": "All constraints passed." if constraint_pass else "At least one constraint failed."
        },
        {
            "criterion": "task report exists",
            "status": "passed" if report_pass else "failed",
            "evidence": str(report_path) if report_pass else "Missing task report."
        }
    ]

    overall = "passed" if command_pass and constraint_pass and report_pass else "failed"

    ledger = {
        "task_id": task,
        "timestamp_utc": dt.datetime.now(dt.UTC).isoformat(),
        "git": {
            "commit_before": git_output(["rev-parse", "HEAD"]),
            "status_porcelain": git_output(["status", "--porcelain"]) or "",
        },
        "changed_files": files,
        "commands": commands,
        "overall_status": overall,
        "acceptance_criteria": acceptance,
        "constraint_check": constraints,
    }

    out = VERIFICATION_DIR / f"task_{task}_verification.json"
    out.write_text(json.dumps(ledger, indent=2), encoding="utf-8")

    print(f"Wrote verification ledger: {out}")
    print(f"Overall status: {overall}")

    return 0 if overall == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
