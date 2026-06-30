import pytest
from pydantic import ValidationError

from app.traces import (
    TraceBatch,
    TraceRecord,
    import_trace_batch,
    select_failed_traces,
    trace_failure_to_test_case,
)
from app.traces.importers import TraceImportError


def test_trace_record_validates_and_dumps_deterministically() -> None:
    record = TraceRecord(
        id="trace-1",
        inputs={"question": "What is 6 * 7?"},
        output="41",
        metadata={"failed": True},
    )

    assert record.model_dump(mode="json") == {
        "id": "trace-1",
        "inputs": {"question": "What is 6 * 7?"},
        "output": "41",
        "error_message": None,
        "metadata": {"failed": True},
    }


@pytest.mark.parametrize(
    "kwargs",
    [
        {"id": " ", "inputs": {"x": 1}, "output": "ok"},
        {"id": "trace-1", "inputs": {}, "output": "ok"},
        {"id": "trace-1", "inputs": {"x": 1}},
        {"id": "trace-1", "inputs": {"x": 1}, "error_message": " "},
    ],
)
def test_trace_record_rejects_invalid_values(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        TraceRecord(**kwargs)


def test_trace_batch_rejects_empty_records_and_duplicate_ids() -> None:
    record = TraceRecord(id="trace-1", inputs={"x": 1}, output="ok")

    with pytest.raises(ValidationError, match="records cannot be empty"):
        TraceBatch(records=[])

    with pytest.raises(ValidationError, match="trace ids must be unique"):
        TraceBatch(records=[record, record])


def test_import_trace_batch_rejects_invalid_payload_shapes() -> None:
    with pytest.raises(TraceImportError, match="trace payload must be an object"):
        import_trace_batch([])

    with pytest.raises(TraceImportError, match="trace payload must include records"):
        import_trace_batch({})

    with pytest.raises(TraceImportError, match="invalid trace payload"):
        import_trace_batch({"records": []})


def test_select_failed_traces_is_deterministic() -> None:
    batch = import_trace_batch(
        {
            "records": [
                {"id": "trace-1", "inputs": {"x": 1}, "output": "ok"},
                {"id": "trace-2", "inputs": {"x": 2}, "output": "bad", "metadata": {"failed": True}},
                {"id": "trace-3", "inputs": {"x": 3}, "error_message": "tool failed"},
            ]
        }
    )

    failed = select_failed_traces(batch)

    assert [record.id for record in failed] == ["trace-2", "trace-3"]


def test_trace_failure_to_test_case_converts_failed_trace() -> None:
    record = TraceRecord(
        id="trace-1",
        inputs={"question": "What is 6 * 7?"},
        output="41",
        metadata={"failed": True},
    )

    test_case = trace_failure_to_test_case(
        record,
        test_case_id="case-1",
        dataset_id="dataset-1",
        expected_output="42",
    )

    assert test_case.model_dump(mode="json") == {
        "id": "case-1",
        "dataset_id": "dataset-1",
        "name": "Trace failure: trace-1",
        "inputs": {"question": "What is 6 * 7?"},
        "expected_output": "42",
    }


def test_trace_failure_to_test_case_rejects_non_failed_trace() -> None:
    record = TraceRecord(id="trace-1", inputs={"x": 1}, output="ok")

    with pytest.raises(ValueError, match="only failed trace records"):
        trace_failure_to_test_case(
            record,
            test_case_id="case-1",
            dataset_id="dataset-1",
        )
