from __future__ import annotations

from typing import Any, Protocol

from app.providers.models import ProviderRequest, ProviderResponse


class OpenAIProviderError(RuntimeError):
    pass


class OpenAIResponsesResource(Protocol):
    def create(self, **kwargs: Any) -> Any:
        pass


class OpenAICompatibleClient(Protocol):
    responses: OpenAIResponsesResource


class OpenAIProvider:
    def __init__(self, client: OpenAICompatibleClient) -> None:
        self.client = client

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        response = self.client.responses.create(
            model=request.model_name,
            input=request.prompt,
            **request.parameters,
        )
        text = _extract_response_text(response)
        if text is None or not text.strip():
            raise OpenAIProviderError("OpenAI response did not include text output")

        return ProviderResponse(
            text=text,
            model_name=str(getattr(response, "model", request.model_name) or request.model_name),
            metadata=_extract_metadata(response),
        )


def _extract_response_text(response: Any) -> str | None:
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str):
        return output_text

    output = getattr(response, "output", None)
    if isinstance(output, list):
        parts: list[str] = []
        for item in output:
            content = getattr(item, "content", None)
            if isinstance(content, list):
                for content_item in content:
                    text = getattr(content_item, "text", None)
                    if isinstance(text, str):
                        parts.append(text)
        if parts:
            return "".join(parts)
    return None


def _extract_metadata(response: Any) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    response_id = getattr(response, "id", None)
    if response_id is not None:
        metadata["response_id"] = str(response_id)
    response_model = getattr(response, "model", None)
    if response_model is not None:
        metadata["response_model"] = str(response_model)
    usage = getattr(response, "usage", None)
    if usage is not None:
        if hasattr(usage, "model_dump"):
            metadata["usage"] = usage.model_dump(mode="json")
        elif isinstance(usage, dict):
            metadata["usage"] = usage
        else:
            metadata["usage"] = str(usage)
    return metadata
