import pytest
from pydantic import ValidationError

from app.providers import (
    FakeProvider,
    NoScriptedResponseError,
    ProviderRequest,
    ProviderResponse,
)


def test_provider_request_dumps_deterministically() -> None:
    request = ProviderRequest(
        prompt="Summarize this trace",
        model_name="fake-model",
        parameters={"temperature": 0, "tags": ["smoke"]},
    )

    assert request.model_dump(mode="json") == {
        "prompt": "Summarize this trace",
        "model_name": "fake-model",
        "parameters": {"temperature": 0, "tags": ["smoke"]},
    }


@pytest.mark.parametrize(
    "kwargs",
    [
        {"prompt": " ", "model_name": "fake-model"},
        {"prompt": "hello", "model_name": " "},
    ],
)
def test_provider_request_rejects_blank_required_text(kwargs: dict[str, str]) -> None:
    with pytest.raises(ValidationError):
        ProviderRequest(**kwargs)


def test_provider_response_dumps_deterministically() -> None:
    response = ProviderResponse(
        text="ok",
        model_name="fake-model",
        metadata={"tokens": 2},
    )

    assert response.model_dump(mode="json") == {
        "text": "ok",
        "model_name": "fake-model",
        "metadata": {"tokens": 2},
    }


@pytest.mark.parametrize(
    "kwargs",
    [
        {"text": " ", "model_name": "fake-model"},
        {"text": "ok", "model_name": " "},
    ],
)
def test_provider_response_rejects_blank_required_text(kwargs: dict[str, str]) -> None:
    with pytest.raises(ValidationError):
        ProviderResponse(**kwargs)


def test_fake_provider_returns_scripted_responses_in_order_and_records_requests() -> None:
    provider = FakeProvider(
        [
            ProviderResponse(text="first", model_name="fake-model", metadata={"index": 1}),
            "second",
        ]
    )
    first_request = ProviderRequest(prompt="prompt 1", model_name="fake-model")
    second_request = ProviderRequest(prompt="prompt 2", model_name="fake-model")

    first_response = provider.generate(first_request)
    second_response = provider.generate(second_request)

    assert first_response.model_dump(mode="json") == {
        "text": "first",
        "model_name": "fake-model",
        "metadata": {"index": 1},
    }
    assert second_response.model_dump(mode="json") == {
        "text": "second",
        "model_name": "fake-model",
        "metadata": {},
    }
    assert provider.requests == [first_request, second_request]


def test_fake_provider_echo_fallback_is_deterministic() -> None:
    provider = FakeProvider()
    request = ProviderRequest(prompt="echo me", model_name="fake-model")

    response = provider.generate(request)

    assert response.model_dump(mode="json") == {
        "text": "echo me",
        "model_name": "fake-model",
        "metadata": {"fake_provider": True, "fallback": "echo"},
    }


def test_fake_provider_can_disable_echo_fallback() -> None:
    provider = FakeProvider(echo_fallback=False)
    request = ProviderRequest(prompt="no response", model_name="fake-model")

    with pytest.raises(NoScriptedResponseError):
        provider.generate(request)

    assert provider.requests == [request]
