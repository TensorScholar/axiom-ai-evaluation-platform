from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, JsonValue, ValidationError, field_validator

from app.evaluations import EvaluationRunSummary


class GateInputError(ValueError):
    pass


def _require_text(value: str) -> str:
    if not value.strip():
        raise ValueError("value cannot be empty")
    return value


class GateModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class GateFailure(GateModel):
    case_id: str
    reason: str

    @field_validator("case_id", "reason")
    @classmethod
    def required_text_must_not_be_empty(cls, value: str) -> str:
        return _require_text(value)


class GateResult(GateModel):
    suite_id: str
    passed: bool
    failures: list[GateFailure] = Field(default_factory=list)
    metrics: dict[str, JsonValue] = Field(default_factory=dict)

    @field_validator("suite_id")
    @classmethod
    def suite_id_must_not_be_empty(cls, value: str) -> str:
        return _require_text(value)


def gate_exit_code(result: GateResult) -> int:
    if result.passed and not result.failures:
        return 0
    return 1


def gate_result_from_summary(
    summary: EvaluationRunSummary,
    *,
    min_pass_rate: float = 1.0,
    max_error_rate: float = 0.0,
) -> GateResult:
    _validate_rate("min_pass_rate", min_pass_rate)
    _validate_rate("max_error_rate", max_error_rate)

    failures: list[GateFailure] = []
    if summary.pass_rate < min_pass_rate:
        failures.append(
            GateFailure(
                case_id=str(summary.run_id),
                reason=f"pass rate {summary.pass_rate:.4f} is below minimum {min_pass_rate:.4f}",
            )
        )
    if summary.error_rate > max_error_rate:
        failures.append(
            GateFailure(
                case_id=str(summary.run_id),
                reason=f"error rate {summary.error_rate:.4f} exceeds maximum {max_error_rate:.4f}",
            )
        )

    return GateResult(
        suite_id=str(summary.run_id),
        passed=not failures,
        failures=failures,
        metrics={
            "pass_rate": summary.pass_rate,
            "error_rate": summary.error_rate,
            "total_samples": summary.total_samples,
            "metric_count": summary.metric_count,
        },
    )


def load_gate_result(path: str | Path) -> GateResult:
    result_path = Path(path)
    try:
        raw = result_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise GateInputError(f"could not read result file: {result_path}") from exc

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise GateInputError(f"invalid JSON in result file: {result_path}") from exc

    try:
        return GateResult.model_validate(payload)
    except ValidationError as exc:
        raise GateInputError(f"invalid gate result structure: {exc}") from exc


def load_evaluation_summary(path: str | Path) -> EvaluationRunSummary:
    summary_path = Path(path)
    try:
        raw = summary_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise GateInputError(f"could not read summary file: {summary_path}") from exc

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise GateInputError(f"invalid JSON in summary file: {summary_path}") from exc

    try:
        return EvaluationRunSummary.model_validate(payload)
    except ValidationError as exc:
        raise GateInputError(f"invalid evaluation summary structure: {exc}") from exc


def write_gate_result(path: str | Path, result: GateResult) -> None:
    output = Path(path)
    try:
        output.write_text(
            json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True),
            encoding="utf-8",
        )
    except OSError as exc:
        raise GateInputError(f"could not write gate result file: {output}") from exc


def _validate_rate(name: str, value: float) -> None:
    if value < 0.0 or value > 1.0:
        raise GateInputError(f"{name} must be between 0.0 and 1.0")
