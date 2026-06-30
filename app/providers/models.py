from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator


def _require_text(value: str) -> str:
    if not value.strip():
        raise ValueError("value cannot be empty")
    return value


class ProviderModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class ProviderRequest(ProviderModel):
    prompt: str
    model_name: str
    parameters: dict[str, JsonValue] = Field(default_factory=dict)

    @field_validator("prompt", "model_name")
    @classmethod
    def required_text_must_not_be_empty(cls, value: str) -> str:
        return _require_text(value)


class ProviderResponse(ProviderModel):
    text: str
    model_name: str
    metadata: dict[str, JsonValue] = Field(default_factory=dict)

    @field_validator("text", "model_name")
    @classmethod
    def required_text_must_not_be_empty(cls, value: str) -> str:
        return _require_text(value)
