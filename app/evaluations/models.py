from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator, model_validator

from app.domain import DatasetId, EvaluationRunId, ProjectId, TestCaseId


class EvaluationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SampleOutcome(str, Enum):
    SUCCEEDED = "succeeded"
    ERRORED = "errored"


def _require_text(value: str) -> str:
    if not value.strip():
        raise ValueError("value cannot be empty")
    return value


class EvaluationModel(BaseModel):
    model_config = ConfigDict(frozen=True, use_enum_values=True)


class EvaluationRunMetadata(EvaluationModel):
    spec_version: str
    code_version: str
    dataset_fingerprint: str
    seed: int
    parameters: dict[str, JsonValue] = Field(default_factory=dict)

    @field_validator("spec_version", "code_version", "dataset_fingerprint")
    @classmethod
    def required_text_must_not_be_empty(cls, value: str) -> str:
        return _require_text(value)

    @field_validator("seed")
    @classmethod
    def seed_must_not_be_negative(cls, value: int) -> int:
        if value < 0:
            raise ValueError("seed cannot be negative")
        return value


class SampleResult(EvaluationModel):
    test_case_id: TestCaseId
    outcome: SampleOutcome
    output: JsonValue | None = None
    error_message: str | None = None
    metadata: dict[str, JsonValue] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_outcome_fields(self) -> "SampleResult":
        if self.outcome == SampleOutcome.ERRORED:
            if self.error_message is None or not self.error_message.strip():
                raise ValueError("errored samples require an error message")
        if self.outcome == SampleOutcome.SUCCEEDED and self.error_message is not None:
            raise ValueError("succeeded samples cannot include an error message")
        return self


class EvaluationRunRecord(EvaluationModel):
    id: EvaluationRunId
    project_id: ProjectId
    dataset_id: DatasetId
    status: EvaluationStatus
    metadata: EvaluationRunMetadata
    sample_results: list[SampleResult] = Field(default_factory=list)
