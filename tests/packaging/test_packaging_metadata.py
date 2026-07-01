from __future__ import annotations

import tomllib
from pathlib import Path

from app.cli import build_parser


ROOT = Path(__file__).resolve().parents[2]


def load_pyproject() -> dict[str, object]:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def test_pyproject_defines_installable_package_metadata() -> None:
    pyproject = load_pyproject()

    assert pyproject["build-system"] == {
        "requires": ["setuptools>=69"],
        "build-backend": "setuptools.build_meta",
    }
    assert pyproject["project"] == {
        "name": "axiom-ai-evaluation-platform",
        "version": "0.5.0",
        "description": "A local evaluation and regression platform for loop-based AI systems and LLM applications.",
        "readme": "README_START_HERE.md",
        "requires-python": ">=3.11",
        "dependencies": ["fastapi", "pydantic", "sqlalchemy"],
        "scripts": {"axiom": "app.cli:main"},
    }


def test_pyproject_package_discovery_includes_app_package() -> None:
    pyproject = load_pyproject()

    assert pyproject["tool"]["setuptools"]["packages"]["find"] == {"include": ["app*"]}


def test_axiom_console_script_points_to_existing_cli_main() -> None:
    pyproject = load_pyproject()

    assert pyproject["project"]["scripts"]["axiom"] == "app.cli:main"
    parser = build_parser()
    assert parser.prog == "axiom"


def test_installation_documentation_names_console_command() -> None:
    install_doc = (ROOT / "INSTALL.md").read_text(encoding="utf-8")

    assert "python3 -m pip install -e ." in install_doc
    assert "axiom --help" in install_doc
    assert "No external provider credentials are required" in install_doc
