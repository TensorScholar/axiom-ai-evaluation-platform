from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.domain import DatasetId, TestCase
from app.regression import RegressionCase, failure_to_regression_case
from app.traces import import_trace_batch, select_failed_traces, trace_failure_to_test_case
from app.traces.importers import TraceImportError
from app.traces.models import TraceRecord


class TraceFileImportError(ValueError):
    pass


class TraceImportOutputKind(str, Enum):
    TEST_CASES = "test-cases"
    REGRESSION_CASES = "regression-cases"


class TraceFileImportResult(BaseModel):
    model_config = ConfigDict(frozen=True, use_enum_values=True)

    output_kind: TraceImportOutputKind
    records_imported: int
    failed_records: int
    items: list[TestCase | RegressionCase] = Field(default_factory=list)

    @field_validator("records_imported", "failed_records")
    @classmethod
    def counts_must_not_be_negative(cls, value: int) -> int:
        if value < 0:
            raise ValueError("count cannot be negative")
        return value


def run_trace_file_import(
    *,
    trace_file: str | Path,
    output_file: str | Path,
    dataset_id: str,
    output_kind: TraceImportOutputKind | str = TraceImportOutputKind.TEST_CASES,
    source_run_id: str | None = None,
) -> TraceFileImportResult:
    kind = _parse_output_kind(output_kind)
    if not dataset_id.strip():
        raise TraceFileImportError("dataset_id is required")
    if kind == TraceImportOutputKind.REGRESSION_CASES and (
        source_run_id is None or not source_run_id.strip()
    ):
        raise TraceFileImportError("source_run_id is required for regression-cases output")

    payload = _load_json_object(trace_file)
    try:
        batch = import_trace_batch(payload)
    except TraceImportError as exc:
        raise TraceFileImportError(str(exc)) from exc
    except ValidationError as exc:
        raise TraceFileImportError(f"invalid trace payload: {exc}") from exc

    failed = select_failed_traces(batch)
    items = _convert_failed_records(
        failed,
        dataset_id=DatasetId(dataset_id),
        output_kind=kind,
        source_run_id=source_run_id,
    )
    result = TraceFileImportResult(
        output_kind=kind,
        records_imported=len(batch.records),
        failed_records=len(failed),
        items=items,
    )
    _write_result(output_file, result)
    return result


def _convert_failed_records(
    records: list[TraceRecord],
    *,
    dataset_id: DatasetId,
    output_kind: TraceImportOutputKind,
    source_run_id: str | None,
) -> list[TestCase | RegressionCase]:
    if output_kind == TraceImportOutputKind.TEST_CASES:
        return [
            trace_failure_to_test_case(
                record,
                test_case_id=_test_case_id(record),
                dataset_id=dataset_id,
            )
            for record in records
        ]

    if source_run_id is None:
        raise TraceFileImportError("source_run_id is required for regression-cases output")

    return [
        failure_to_regression_case(
            regression_case_id=_regression_case_id(record),
            source_run_id=source_run_id,
            test_case_id=_test_case_id(record),
            dataset_id=dataset_id,
            name=f"Trace failure: {record.id}",
            inputs=record.inputs,
            failure_reason=_failure_reason(record),
        )
        for record in records
    ]


def _load_json_object(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    try:
        raw = source.read_text(encoding="utf-8")
    except OSError as exc:
        raise TraceFileImportError(f"could not read trace file: {source}") from exc

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise TraceFileImportError(f"invalid JSON in trace file: {source}") from exc

    if not isinstance(payload, dict):
        raise TraceFileImportError("trace file must contain a JSON object")
    return payload


def _write_result(path: str | Path, result: TraceFileImportResult) -> None:
    output = Path(path)
    try:
        output.write_text(
            json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True),
            encoding="utf-8",
        )
    except OSError as exc:
        raise TraceFileImportError(f"could not write trace import result: {output}") from exc


def _parse_output_kind(value: TraceImportOutputKind | str) -> TraceImportOutputKind:
    try:
        return TraceImportOutputKind(value)
    except ValueError as exc:
        raise TraceFileImportError(f"unsupported output_kind: {value}") from exc


def _test_case_id(record: TraceRecord) -> str:
    return f"trace-case-{record.id}"


def _regression_case_id(record: TraceRecord) -> str:
    return f"trace-regression-{record.id}"


def _failure_reason(record: TraceRecord) -> str:
    if record.error_message is not None:
        return record.error_message
    return "trace marked failed"
