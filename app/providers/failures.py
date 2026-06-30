from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, field_validator


class ProviderFailureCategory(str, Enum):
    VALIDATION = "validation"
    AUTH = "auth"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class ProviderFailure(BaseModel):
    model_config = ConfigDict(frozen=True, use_enum_values=True)

    provider_name: str
    category: ProviderFailureCategory
    message: str
    exception_type: str

    @field_validator("provider_name", "message", "exception_type")
    @classmethod
    def required_text_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("value cannot be empty")
        return value


def classify_provider_exception(
    exc: Exception,
    *,
    provider_name: str,
) -> ProviderFailure:
    exception_type = exc.__class__.__name__
    message = str(exc) or exception_type
    category = _category_from_exception(exception_type, message)
    return ProviderFailure(
        provider_name=provider_name,
        category=category,
        message=message,
        exception_type=exception_type,
    )


def _category_from_exception(exception_type: str, message: str) -> ProviderFailureCategory:
    haystack = f"{exception_type} {message}".lower()
    if "auth" in haystack or "permission" in haystack or "unauthorized" in haystack or "api key" in haystack:
        return ProviderFailureCategory.AUTH
    if "rate" in haystack and "limit" in haystack:
        return ProviderFailureCategory.RATE_LIMIT
    if "timeout" in haystack or "timed out" in haystack:
        return ProviderFailureCategory.TIMEOUT
    if "validation" in haystack or "invalid" in haystack or "bad request" in haystack:
        return ProviderFailureCategory.VALIDATION
    return ProviderFailureCategory.UNKNOWN
