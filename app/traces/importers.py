from __future__ import annotations

from app.domain import DatasetId, TestCase, TestCaseId
from app.traces.models import TraceBatch, TraceRecord


class TraceImportError(ValueError):
    pass


def import_trace_batch(payload: object) -> TraceBatch:
    if not isinstance(payload, dict):
        raise TraceImportError("trace payload must be an object")
    if "records" not in payload:
        raise TraceImportError("trace payload must include records")
    try:
        return TraceBatch.model_validate(payload)
    except ValueError as exc:
        raise TraceImportError(f"invalid trace payload: {exc}") from exc


def select_failed_traces(batch: TraceBatch) -> list[TraceRecord]:
    return [record for record in batch.records if _is_failed_trace(record)]


def trace_failure_to_test_case(
    record: TraceRecord,
    *,
    test_case_id: TestCaseId,
    dataset_id: DatasetId,
    name: str | None = None,
    expected_output: str | None = None,
) -> TestCase:
    if not _is_failed_trace(record):
        raise ValueError("only failed trace records can be converted into failure test cases")

    return TestCase(
        id=test_case_id,
        dataset_id=dataset_id,
        name=name or f"Trace failure: {record.id}",
        inputs=record.inputs,
        expected_output=expected_output,
    )


def _is_failed_trace(record: TraceRecord) -> bool:
    return record.error_message is not None or record.metadata.get("failed") is True
