from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator, model_validator


def _require_text(value: str) -> str:
    if not value.strip():
        raise ValueError("value cannot be empty")
    return value


class TraceModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class TraceRecord(TraceModel):
    id: str
    inputs: dict[str, JsonValue]
    output: JsonValue | None = None
    error_message: str | None = None
    metadata: dict[str, JsonValue] = Field(default_factory=dict)

    @field_validator("id")
    @classmethod
    def id_must_not_be_empty(cls, value: str) -> str:
        return _require_text(value)

    @field_validator("inputs")
    @classmethod
    def inputs_must_not_be_empty(cls, value: dict[str, JsonValue]) -> dict[str, JsonValue]:
        if not value:
            raise ValueError("inputs cannot be empty")
        return value

    @field_validator("error_message")
    @classmethod
    def error_message_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is not None:
            return _require_text(value)
        return value

    @model_validator(mode="after")
    def output_or_error_must_exist(self) -> "TraceRecord":
        if self.output is None and self.error_message is None:
            raise ValueError("trace record requires output or error message")
        return self


class TraceBatch(TraceModel):
    records: list[TraceRecord]

    @model_validator(mode="after")
    def records_must_be_non_empty_and_unique(self) -> "TraceBatch":
        if not self.records:
            raise ValueError("records cannot be empty")
        ids = [record.id for record in self.records]
        if len(ids) != len(set(ids)):
            raise ValueError("trace ids must be unique")
        return self
