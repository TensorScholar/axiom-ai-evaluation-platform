import json

import pytest

from app.trace_file_import import TraceFileImportError, run_trace_file_import


def write_json(path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def trace_fixture() -> dict[str, object]:
    return {
        "records": [
            {"id": "trace-1", "inputs": {"prompt": "ok"}, "output": "ok"},
            {
                "id": "trace-2",
                "inputs": {"prompt": "bad"},
                "output": "bad answer",
                "metadata": {"failed": True},
            },
            {
                "id": "trace-3",
                "inputs": {"prompt": "tool"},
                "error_message": "tool failed",
            },
        ]
    }


def test_run_trace_file_import_writes_failed_trace_test_cases(tmp_path) -> None:
    trace_file = tmp_path / "traces.json"
    output_file = tmp_path / "cases.json"
    write_json(trace_file, trace_fixture())

    result = run_trace_file_import(
        trace_file=trace_file,
        output_file=output_file,
        dataset_id="dataset-1",
    )

    payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert result.records_imported == 3
    assert result.failed_records == 2
    assert payload == {
        "failed_records": 2,
        "items": [
            {
                "dataset_id": "dataset-1",
                "expected_output": None,
                "id": "trace-case-trace-2",
                "inputs": {"prompt": "bad"},
                "name": "Trace failure: trace-2",
            },
            {
                "dataset_id": "dataset-1",
                "expected_output": None,
                "id": "trace-case-trace-3",
                "inputs": {"prompt": "tool"},
                "name": "Trace failure: trace-3",
            },
        ],
        "output_kind": "test-cases",
        "records_imported": 3,
    }


def test_run_trace_file_import_writes_regression_cases(tmp_path) -> None:
    trace_file = tmp_path / "traces.json"
    output_file = tmp_path / "regressions.json"
    write_json(trace_file, trace_fixture())

    run_trace_file_import(
        trace_file=trace_file,
        output_file=output_file,
        dataset_id="dataset-1",
        output_kind="regression-cases",
        source_run_id="run-050",
    )

    payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert payload["output_kind"] == "regression-cases"
    assert payload["records_imported"] == 3
    assert payload["failed_records"] == 2
    assert payload["items"][0] == {
        "failure_reason": "trace marked failed",
        "id": "trace-regression-trace-2",
        "source_run_id": "run-050",
        "test_case": {
            "dataset_id": "dataset-1",
            "expected_output": None,
            "id": "trace-case-trace-2",
            "inputs": {"prompt": "bad"},
            "name": "Trace failure: trace-2",
        },
    }
    assert payload["items"][1]["failure_reason"] == "tool failed"


def test_run_trace_file_import_requires_source_run_for_regression_cases(tmp_path) -> None:
    trace_file = tmp_path / "traces.json"
    output_file = tmp_path / "regressions.json"
    write_json(trace_file, trace_fixture())

    with pytest.raises(TraceFileImportError, match="source_run_id is required"):
        run_trace_file_import(
            trace_file=trace_file,
            output_file=output_file,
            dataset_id="dataset-1",
            output_kind="regression-cases",
        )


def test_run_trace_file_import_rejects_invalid_trace_file(tmp_path) -> None:
    trace_file = tmp_path / "traces.json"
    output_file = tmp_path / "cases.json"
    write_json(trace_file, {"records": []})

    with pytest.raises(TraceFileImportError, match="invalid trace payload"):
        run_trace_file_import(
            trace_file=trace_file,
            output_file=output_file,
            dataset_id="dataset-1",
        )
