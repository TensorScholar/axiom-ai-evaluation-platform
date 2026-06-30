from __future__ import annotations

from collections.abc import Iterable

from app.judges.models import JudgeRequest, JudgeResult


class NoScriptedJudgeResultError(RuntimeError):
    pass


class ScriptedJudge:
    def __init__(self, scripted_results: Iterable[JudgeResult]) -> None:
        self._scripted_results = list(scripted_results)
        self.requests: list[JudgeRequest] = []

    def judge(self, request: JudgeRequest) -> JudgeResult:
        self.requests.append(request)

        if not self._scripted_results:
            raise NoScriptedJudgeResultError("scripted judge has no results remaining")

        return self._scripted_results.pop(0)
