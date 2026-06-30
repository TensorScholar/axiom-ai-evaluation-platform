from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.domain import EvaluationRunId, TestCase


def _require_text(value: str) -> str:
    if not value.strip():
        raise ValueError("value cannot be empty")
    return value


class RegressionModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class RegressionCase(RegressionModel):
    id: str
    source_run_id: EvaluationRunId
    test_case: TestCase
    failure_reason: str

    @field_validator("id", "failure_reason")
    @classmethod
    def required_text_must_not_be_empty(cls, value: str) -> str:
        return _require_text(value)


class RegressionSuite(RegressionModel):
    id: str
    name: str
    cases: list[RegressionCase]

    @field_validator("id", "name")
    @classmethod
    def required_text_must_not_be_empty(cls, value: str) -> str:
        return _require_text(value)

    @model_validator(mode="after")
    def cases_must_be_non_empty_and_unique(self) -> "RegressionSuite":
        if not self.cases:
            raise ValueError("cases cannot be empty")
        case_ids = [case.id for case in self.cases]
        if len(case_ids) != len(set(case_ids)):
            raise ValueError("case ids must be unique")
        return self


class RegressionRerunPlan(RegressionModel):
    suite_id: str
    model_name: str
    prompt_version: str
    case_ids: list[str]

    @field_validator("suite_id", "model_name", "prompt_version")
    @classmethod
    def required_text_must_not_be_empty(cls, value: str) -> str:
        return _require_text(value)

    @field_validator("case_ids")
    @classmethod
    def case_ids_must_not_be_empty(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("case ids cannot be empty")
        for case_id in value:
            _require_text(case_id)
        return value
