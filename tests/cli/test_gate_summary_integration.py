import json
from io import StringIO

import pytest

from app.ci_gate import GateInputError, gate_result_from_summary
from app.cli import main
from app.evaluations import EvaluationRunSummary, EvaluationStatus


def make_summary(**overrides) -> EvaluationRunSummary:
    payload = {
        "run_id": "run-021",
        "status": EvaluationStatus.COMPLETED,
        "total_samples": 2,
        "succeeded_samples": 2,
        "errored_samples": 0,
        "metric_count": 2,
        "passed_metrics": 2,
        "failed_metrics": 0,
        "pass_rate": 1.0,
        "error_rate": 0.0,
    }
    payload.update(overrides)
    return EvaluationRunSummary(**payload)


def test_gate_result_from_summary_passes_when_thresholds_are_met() -> None:
    result = gate_result_from_summary(make_summary(), min_pass_rate=1.0, max_error_rate=0.0)

    assert result.model_dump(mode="json") == {
        "suite_id": "run-021",
        "passed": True,
        "failures": [],
        "metrics": {
            "pass_rate": 1.0,
            "error_rate": 0.0,
            "total_samples": 2,
            "metric_count": 2,
        },
    }


def test_gate_result_from_summary_fails_with_clear_reasons() -> None:
    result = gate_result_from_summary(
        make_summary(pass_rate=0.5, error_rate=0.25, passed_metrics=1, failed_metrics=1),
        min_pass_rate=0.75,
        max_error_rate=0.1,
    )

    assert not result.passed
    assert [failure.reason for failure in result.failures] == [
        "pass rate 0.5000 is below minimum 0.7500",
        "error rate 0.2500 exceeds maximum 0.1000",
    ]


def test_gate_result_from_summary_rejects_invalid_thresholds() -> None:
    with pytest.raises(GateInputError, match="min_pass_rate"):
        gate_result_from_summary(make_summary(), min_pass_rate=1.1)

    with pytest.raises(GateInputError, match="max_error_rate"):
        gate_result_from_summary(make_summary(), max_error_rate=-0.1)


def test_summarize_gate_cli_writes_gate_result(tmp_path) -> None:
    summary_file = tmp_path / "summary.json"
    output_file = tmp_path / "gate.json"
    summary_file.write_text(json.dumps(make_summary().model_dump(mode="json")), encoding="utf-8")
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "summarize-gate",
            "--summary-file",
            str(summary_file),
            "--output-file",
            str(output_file),
            "--min-pass-rate",
            "1.0",
            "--max-error-rate",
            "0.0",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    result = json.loads(output_file.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert stdout.getvalue() == "AXIOM gate result written: run-021\n"
    assert stderr.getvalue() == ""
    assert result["passed"] is True


def test_summarize_gate_cli_returns_two_for_invalid_summary(tmp_path) -> None:
    summary_file = tmp_path / "summary.json"
    output_file = tmp_path / "gate.json"
    summary_file.write_text(json.dumps({"run_id": " "}), encoding="utf-8")
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "summarize-gate",
            "--summary-file",
            str(summary_file),
            "--output-file",
            str(output_file),
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert stderr.getvalue().startswith("AXIOM summarize-gate error:")
