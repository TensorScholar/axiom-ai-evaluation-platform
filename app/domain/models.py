from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator

from app.domain.identifiers import (
    DatasetId,
    EvaluationRunId,
    ProjectId,
    RubricId,
    TestCaseId,
)


def _require_text(value: str) -> str:
    if not value.strip():
        raise ValueError("value cannot be empty")
    return value


class DomainModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class Project(DomainModel):
    id: ProjectId
    name: str

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, value: str) -> str:
        return _require_text(value)


class Dataset(DomainModel):
    id: DatasetId
    project_id: ProjectId
    name: str

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, value: str) -> str:
        return _require_text(value)


class TestCase(DomainModel):
    id: TestCaseId
    dataset_id: DatasetId
    name: str
    inputs: dict[str, Any]
    expected_output: str | None = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, value: str) -> str:
        return _require_text(value)

    @field_validator("inputs")
    @classmethod
    def inputs_must_not_be_empty(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not value:
            raise ValueError("inputs cannot be empty")
        return value


class Rubric(DomainModel):
    id: RubricId
    project_id: ProjectId
    name: str
    criteria: list[str]

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, value: str) -> str:
        return _require_text(value)

    @field_validator("criteria")
    @classmethod
    def criteria_must_not_be_empty(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("criteria cannot be empty")
        for criterion in value:
            _require_text(criterion)
        return value


class EvaluationRunReference(DomainModel):
    id: EvaluationRunId
    project_id: ProjectId
    dataset_id: DatasetId
