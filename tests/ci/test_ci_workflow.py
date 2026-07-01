from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


def workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_ci_workflow_exists_and_runs_on_main_and_pull_requests() -> None:
    text = workflow_text()

    assert "name: CI" in text
    assert 'branches: ["main"]' in text
    assert "pull_request:" in text


def test_ci_workflow_sets_up_python_and_installs_local_package() -> None:
    text = workflow_text()

    assert "actions/checkout@v4" in text
    assert "actions/setup-python@v5" in text
    assert 'python-version: "3.12"' in text
    assert "python -m pip install -e . pytest httpx" in text


def test_ci_workflow_runs_tests_and_compile_check() -> None:
    text = workflow_text()

    assert "python -m pytest" in text
    assert "python -m compileall app" in text


def test_ci_workflow_avoids_deployment_and_external_service_steps() -> None:
    text = workflow_text().lower()
    forbidden_terms = [
        "deploy",
        "docker",
        "terraform",
        "kubectl",
        "helm",
        "aws",
        "gcloud",
        "azure",
        "secrets.",
    ]

    for term in forbidden_terms:
        assert term not in text
