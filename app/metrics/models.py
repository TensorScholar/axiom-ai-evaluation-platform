from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator


class MetricResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    passed: bool
    score: float = Field(ge=0.0, le=1.0)
    details: dict[str, JsonValue] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("name cannot be empty")
        return value
