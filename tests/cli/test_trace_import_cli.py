import json
from io import StringIO

from app.cli import main


def write_json(path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_trace_import_cli_writes_failed_trace_test_cases(tmp_path) -> None:
    trace_file = tmp_path / "traces.json"
    output_file = tmp_path / "cases.json"
    write_json(
        trace_file,
        {
            "records": [
                {"id": "trace-1", "inputs": {"x": 1}, "output": "ok"},
                {"id": "trace-2", "inputs": {"x": 2}, "error_message": "failed"},
            ]
        },
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "trace-import",
            "--trace-file",
            str(trace_file),
            "--output-file",
            str(output_file),
            "--dataset-id",
            "dataset-1",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert stdout.getvalue() == "AXIOM trace import completed: 1 failed of 2 records\n"
    assert stderr.getvalue() == ""
    assert payload["output_kind"] == "test-cases"
    assert payload["items"][0]["id"] == "trace-case-trace-2"


def test_trace_import_cli_writes_regression_cases(tmp_path) -> None:
    trace_file = tmp_path / "traces.json"
    output_file = tmp_path / "regressions.json"
    write_json(
        trace_file,
        {
            "records": [
                {
                    "id": "trace-1",
                    "inputs": {"x": 1},
                    "output": "bad",
                    "metadata": {"failed": True},
                }
            ]
        },
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "trace-import",
            "--trace-file",
            str(trace_file),
            "--output-file",
            str(output_file),
            "--dataset-id",
            "dataset-1",
            "--output-kind",
            "regression-cases",
            "--source-run-id",
            "run-050",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert stdout.getvalue() == "AXIOM trace import completed: 1 failed of 1 records\n"
    assert stderr.getvalue() == ""
    assert payload["items"][0]["id"] == "trace-regression-trace-1"
    assert payload["items"][0]["source_run_id"] == "run-050"


def test_trace_import_cli_returns_two_for_invalid_trace_file(tmp_path) -> None:
    trace_file = tmp_path / "traces.json"
    output_file = tmp_path / "cases.json"
    write_json(trace_file, {"records": []})
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "trace-import",
            "--trace-file",
            str(trace_file),
            "--output-file",
            str(output_file),
            "--dataset-id",
            "dataset-1",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert stderr.getvalue().startswith("AXIOM trace-import error:")
