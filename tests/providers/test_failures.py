import pytest
from pydantic import ValidationError

from app.providers import ProviderFailure, ProviderFailureCategory, classify_provider_exception


class AuthenticationError(Exception):
    pass


class RateLimitError(Exception):
    pass


class TimeoutError(Exception):
    pass


class ValidationErrorLike(Exception):
    pass


def test_provider_failure_validates_and_dumps_deterministically() -> None:
    failure = ProviderFailure(
        provider_name="openai",
        category=ProviderFailureCategory.AUTH,
        message="bad api key",
        exception_type="AuthenticationError",
    )

    assert failure.model_dump(mode="json") == {
        "provider_name": "openai",
        "category": "auth",
        "message": "bad api key",
        "exception_type": "AuthenticationError",
    }

    invalid_values = [
        {"provider_name": " ", "message": "x", "exception_type": "E"},
        {"provider_name": "openai", "message": " ", "exception_type": "E"},
        {"provider_name": "openai", "message": "x", "exception_type": " "},
    ]
    for values in invalid_values:
        with pytest.raises(ValidationError):
            ProviderFailure(category=ProviderFailureCategory.AUTH, **values)


def test_classify_provider_exception_categories() -> None:
    cases = [
        (AuthenticationError("invalid api key"), ProviderFailureCategory.AUTH),
        (RateLimitError("rate limit exceeded"), ProviderFailureCategory.RATE_LIMIT),
        (TimeoutError("request timed out"), ProviderFailureCategory.TIMEOUT),
        (ValidationErrorLike("invalid payload"), ProviderFailureCategory.VALIDATION),
        (RuntimeError("something else"), ProviderFailureCategory.UNKNOWN),
    ]

    for exc, expected in cases:
        failure = classify_provider_exception(exc, provider_name="openai")
        assert failure.category == expected
        assert failure.provider_name == "openai"
        assert failure.exception_type == exc.__class__.__name__


def test_classify_provider_exception_rejects_blank_provider_name() -> None:
    with pytest.raises(ValidationError):
        classify_provider_exception(RuntimeError("boom"), provider_name=" ")
