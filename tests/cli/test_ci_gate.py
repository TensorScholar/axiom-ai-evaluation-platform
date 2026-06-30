import json
from io import StringIO

from pydantic import ValidationError
import pytest

from app.ci_gate import GateFailure, GateResult, gate_exit_code, load_gate_result
from app.cli import main


def test_gate_failure_validates_and_dumps_deterministically() -> None:
    failure = GateFailure(case_id="regression-1", reason="score below threshold")

    assert failure.model_dump(mode="json") == {
        "case_id": "regression-1",
        "reason": "score below threshold",
    }

    with pytest.raises(ValidationError):
        GateFailure(case_id=" ", reason="failed")

    with pytest.raises(ValidationError):
        GateFailure(case_id="regression-1", reason=" ")


def test_gate_result_validates_and_dumps_deterministically() -> None:
    result = GateResult(
        suite_id="suite-1",
        passed=False,
        failures=[GateFailure(case_id="regression-1", reason="failed")],
        metrics={"pass_rate": 0.5},
    )

    assert result.model_dump(mode="json") == {
        "suite_id": "suite-1",
        "passed": False,
        "failures": [{"case_id": "regression-1", "reason": "failed"}],
        "metrics": {"pass_rate": 0.5},
    }

    with pytest.raises(ValidationError):
        GateResult(suite_id=" ", passed=True)


def test_gate_exit_code_uses_passed_flag_and_failures() -> None:
    assert gate_exit_code(GateResult(suite_id="suite-1", passed=True)) == 0
    assert gate_exit_code(GateResult(suite_id="suite-1", passed=False)) == 1
    assert (
        gate_exit_code(
            GateResult(
                suite_id="suite-1",
                passed=True,
                failures=[GateFailure(case_id="regression-1", reason="failed")],
            )
        )
        == 1
    )


def test_load_gate_result_reads_valid_json(tmp_path) -> None:
    result_file = tmp_path / "gate.json"
    result_file.write_text(
        json.dumps({"suite_id": "suite-1", "passed": True, "failures": [], "metrics": {}}),
        encoding="utf-8",
    )

    assert load_gate_result(result_file) == GateResult(suite_id="suite-1", passed=True)


def test_cli_returns_zero_for_passing_gate(tmp_path) -> None:
    result_file = tmp_path / "gate.json"
    result_file.write_text(json.dumps({"suite_id": "suite-1", "passed": True}), encoding="utf-8")
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["gate", "--result-file", str(result_file)], stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stdout.getvalue() == "AXIOM gate passed: suite-1\n"
    assert stderr.getvalue() == ""


def test_cli_returns_one_for_failing_gate(tmp_path) -> None:
    result_file = tmp_path / "gate.json"
    result_file.write_text(
        json.dumps(
            {
                "suite_id": "suite-1",
                "passed": False,
                "failures": [{"case_id": "regression-1", "reason": "failed"}],
            }
        ),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["gate", "--result-file", str(result_file)], stdout=stdout, stderr=stderr)

    assert exit_code == 1
    assert stdout.getvalue() == "AXIOM gate failed: suite-1\n"
    assert stderr.getvalue() == ""


def test_cli_returns_two_for_missing_invalid_or_malformed_result_files(tmp_path) -> None:
    missing = tmp_path / "missing.json"
    invalid_json = tmp_path / "invalid.json"
    malformed = tmp_path / "malformed.json"
    invalid_json.write_text("{", encoding="utf-8")
    malformed.write_text(json.dumps({"suite_id": " ", "passed": True}), encoding="utf-8")

    for result_file in [missing, invalid_json, malformed]:
        stdout = StringIO()
        stderr = StringIO()

        exit_code = main(["gate", "--result-file", str(result_file)], stdout=stdout, stderr=stderr)

        assert exit_code == 2
        assert stdout.getvalue() == ""
        assert stderr.getvalue().startswith("AXIOM gate error:")
