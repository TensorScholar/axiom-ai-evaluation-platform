from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator

from app.domain import RubricId, TestCaseId


class JudgeVerdict(str, Enum):
    PASSED = "passed"
    FAILED = "failed"


def _require_text(value: str) -> str:
    if not value.strip():
        raise ValueError("value cannot be empty")
    return value


class JudgeModel(BaseModel):
    model_config = ConfigDict(frozen=True, use_enum_values=True)


class RubricVersion(JudgeModel):
    rubric_id: RubricId
    version: str
    criteria: list[str]

    @field_validator("version")
    @classmethod
    def version_must_not_be_empty(cls, value: str) -> str:
        return _require_text(value)

    @field_validator("criteria")
    @classmethod
    def criteria_must_not_be_empty(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("criteria cannot be empty")
        for criterion in value:
            _require_text(criterion)
        return value


class JudgeRequest(JudgeModel):
    test_case_id: TestCaseId
    rubric: RubricVersion
    prompt: str
    output: str
    expected_output: str | None = None

    @field_validator("prompt", "output")
    @classmethod
    def required_text_must_not_be_empty(cls, value: str) -> str:
        return _require_text(value)


class JudgeResult(JudgeModel):
    test_case_id: TestCaseId
    rubric_id: RubricId
    rubric_version: str
    verdict: JudgeVerdict
    score: float = Field(ge=0.0, le=1.0)
    rationale: str
    criteria_scores: dict[str, float]
    metadata: dict[str, JsonValue] = Field(default_factory=dict)

    @field_validator("rubric_version", "rationale")
    @classmethod
    def required_text_must_not_be_empty(cls, value: str) -> str:
        return _require_text(value)

    @field_validator("criteria_scores")
    @classmethod
    def criteria_scores_must_be_valid(cls, value: dict[str, float]) -> dict[str, float]:
        for criterion, score in value.items():
            _require_text(criterion)
            if score < 0.0 or score > 1.0:
                raise ValueError("criteria scores must be between 0.0 and 1.0")
        return value
