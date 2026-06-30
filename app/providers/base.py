from __future__ import annotations

from typing import Protocol

from app.providers.models import ProviderRequest, ProviderResponse


class ProviderAdapter(Protocol):
    def generate(self, request: ProviderRequest) -> ProviderResponse:
        """Generate a provider response for a typed request."""
