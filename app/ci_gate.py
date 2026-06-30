from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, JsonValue, ValidationError, field_validator


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
