import pytest

from app.providers import OpenAIProvider, OpenAIProviderError, ProviderRequest


class FakeResponses:
    def __init__(self, response) -> None:
        self.response = response
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


class FakeClient:
    def __init__(self, response) -> None:
        self.responses = FakeResponses(response)


class FakeUsage:
    def model_dump(self, mode: str):
        assert mode == "json"
        return {"input_tokens": 3, "output_tokens": 2}


class FakeResponse:
    id = "resp-1"
    model = "gpt-test"
    output_text = "hello"
    usage = FakeUsage()


class EmptyResponse:
    id = "resp-empty"
    model = "gpt-test"
    output_text = ""


def test_openai_provider_calls_responses_create_and_converts_response() -> None:
    client = FakeClient(FakeResponse())
    provider = OpenAIProvider(client)
    request = ProviderRequest(
        prompt="Say hello",
        model_name="gpt-test",
        parameters={"temperature": 0, "max_output_tokens": 20},
    )

    response = provider.generate(request)

    assert client.responses.calls == [
        {
            "model": "gpt-test",
            "input": "Say hello",
            "temperature": 0,
            "max_output_tokens": 20,
        }
    ]
    assert response.model_dump(mode="json") == {
        "text": "hello",
        "model_name": "gpt-test",
        "metadata": {
            "response_id": "resp-1",
            "response_model": "gpt-test",
            "usage": {"input_tokens": 3, "output_tokens": 2},
        },
    }


def test_openai_provider_requires_explicit_client() -> None:
    with pytest.raises(TypeError):
        OpenAIProvider()


def test_openai_provider_raises_clear_error_for_missing_text() -> None:
    provider = OpenAIProvider(FakeClient(EmptyResponse()))

    with pytest.raises(OpenAIProviderError, match="did not include text output"):
        provider.generate(ProviderRequest(prompt="Say hello", model_name="gpt-test"))
