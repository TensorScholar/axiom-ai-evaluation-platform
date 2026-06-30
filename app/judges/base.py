from __future__ import annotations

from typing import Protocol

from app.judges.models import JudgeRequest, JudgeResult


class JudgeAdapter(Protocol):
    def judge(self, request: JudgeRequest) -> JudgeResult:
        """Return a structured judge result for a typed request."""
