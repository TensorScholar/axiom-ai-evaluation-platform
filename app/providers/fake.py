from __future__ import annotations

from collections.abc import Iterable

from app.providers.models import ProviderRequest, ProviderResponse


class NoScriptedResponseError(RuntimeError):
    pass


class FakeProvider:
    def __init__(
        self,
        scripted_responses: Iterable[ProviderResponse | str] = (),
        *,
        echo_fallback: bool = True,
    ) -> None:
        self._scripted_responses = list(scripted_responses)
        self._echo_fallback = echo_fallback
        self.requests: list[ProviderRequest] = []

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        self.requests.append(request)

        if self._scripted_responses:
            response = self._scripted_responses.pop(0)
            if isinstance(response, ProviderResponse):
                return response
            return ProviderResponse(text=response, model_name=request.model_name)

        if self._echo_fallback:
            return ProviderResponse(
                text=request.prompt,
                model_name=request.model_name,
                metadata={"fake_provider": True, "fallback": "echo"},
            )

        raise NoScriptedResponseError("fake provider has no scripted responses remaining")
