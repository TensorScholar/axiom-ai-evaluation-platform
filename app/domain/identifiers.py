from __future__ import annotations

from pydantic_core import core_schema


class DomainId(str):
    """Base class for explicit domain identifiers."""

    def __new__(cls, value: str) -> "DomainId":
        if not isinstance(value, str):
            raise TypeError(f"{cls.__name__} must be a string")
        if not value.strip():
            raise ValueError(f"{cls.__name__} cannot be empty")
        return str.__new__(cls, value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: object,
        handler: object,
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(cls, core_schema.str_schema())


class ProjectId(DomainId):
    pass


class DatasetId(DomainId):
    pass


class TestCaseId(DomainId):
    pass


class RubricId(DomainId):
    pass


class EvaluationRunId(DomainId):
    pass
