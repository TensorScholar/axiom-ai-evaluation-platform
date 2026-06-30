from __future__ import annotations

from pydantic import BaseModel, ConfigDict, JsonValue, field_validator

from app.domain import EvaluationRunId, TestCaseId
from app.evaluations import SampleOutcome


class QueryModel(BaseModel):
    model_config = ConfigDict(frozen=True, use_enum_values=True)


class FailedSampleRecord(QueryModel):
    run_id: EvaluationRunId
    test_case_id: TestCaseId
    outcome: SampleOutcome
    output: JsonValue | None = None
    error_message: str | None = None
    reason: str

    @field_validator("reason")
    @classmethod
    def reason_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("reason cannot be empty")
        return value


class RegressionCandidate(QueryModel):
    run_id: EvaluationRunId
    test_case_id: TestCaseId
    failure_reason: str

    @field_validator("failure_reason")
    @classmethod
    def failure_reason_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("failure reason cannot be empty")
        return value
