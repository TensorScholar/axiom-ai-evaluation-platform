import pytest
from pydantic import ValidationError

from app.judges import (
    JudgeRequest,
    JudgeResult,
    JudgeVerdict,
    NoScriptedJudgeResultError,
    RubricVersion,
    ScriptedJudge,
)


def make_rubric() -> RubricVersion:
    return RubricVersion(
        rubric_id="rubric-1",
        version="v1",
        criteria=["correctness", "conciseness"],
    )


def make_request() -> JudgeRequest:
    return JudgeRequest(
        test_case_id="case-1",
        rubric=make_rubric(),
        prompt="Answer the question",
        output="The answer is 42",
        expected_output="42",
    )


def make_result(verdict: JudgeVerdict = JudgeVerdict.PASSED) -> JudgeResult:
    return JudgeResult(
        test_case_id="case-1",
        rubric_id="rubric-1",
        rubric_version="v1",
        verdict=verdict,
        score=1.0 if verdict == JudgeVerdict.PASSED else 0.0,
        rationale="The output satisfies the rubric.",
        criteria_scores={"correctness": 1.0, "conciseness": 1.0},
        metadata={"judge": "scripted"},
    )


def test_rubric_version_validates_and_dumps_deterministically() -> None:
    rubric = make_rubric()

    assert rubric.model_dump(mode="json") == {
        "rubric_id": "rubric-1",
        "version": "v1",
        "criteria": ["correctness", "conciseness"],
    }


@pytest.mark.parametrize(
    "kwargs",
    [
        {"rubric_id": "rubric-1", "version": " ", "criteria": ["correctness"]},
        {"rubric_id": "rubric-1", "version": "v1", "criteria": []},
        {"rubric_id": "rubric-1", "version": "v1", "criteria": [" "]},
    ],
)
def test_rubric_version_rejects_invalid_values(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        RubricVersion(**kwargs)


def test_judge_request_validates_and_dumps_deterministically() -> None:
    request = make_request()

    assert request.model_dump(mode="json") == {
        "test_case_id": "case-1",
        "rubric": {
            "rubric_id": "rubric-1",
            "version": "v1",
            "criteria": ["correctness", "conciseness"],
        },
        "prompt": "Answer the question",
        "output": "The answer is 42",
        "expected_output": "42",
    }


@pytest.mark.parametrize(
    "kwargs",
    [
        {"test_case_id": "case-1", "rubric": make_rubric(), "prompt": " ", "output": "ok"},
        {"test_case_id": "case-1", "rubric": make_rubric(), "prompt": "prompt", "output": " "},
    ],
)
def test_judge_request_rejects_blank_prompt_or_output(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        JudgeRequest(**kwargs)


def test_judge_result_validates_and_dumps_deterministically() -> None:
    result = make_result()

    assert result.model_dump(mode="json") == {
        "test_case_id": "case-1",
        "rubric_id": "rubric-1",
        "rubric_version": "v1",
        "verdict": "passed",
        "score": 1.0,
        "rationale": "The output satisfies the rubric.",
        "criteria_scores": {"correctness": 1.0, "conciseness": 1.0},
        "metadata": {"judge": "scripted"},
    }


@pytest.mark.parametrize(
    "kwargs",
    [
        {"score": 1.2},
        {"rationale": " "},
        {"criteria_scores": {"correctness": -0.1}},
        {"criteria_scores": {" ": 1.0}},
    ],
)
def test_judge_result_rejects_invalid_values(kwargs: dict[str, object]) -> None:
    base = make_result().model_dump()
    base.update(kwargs)

    with pytest.raises(ValidationError):
        JudgeResult(**base)


def test_scripted_judge_returns_results_in_order_and_records_requests() -> None:
    first = make_result(JudgeVerdict.PASSED)
    second = make_result(JudgeVerdict.FAILED)
    judge = ScriptedJudge([first, second])
    request = make_request()

    assert judge.judge(request) == first
    assert judge.judge(request) == second
    assert judge.requests == [request, request]


def test_scripted_judge_raises_when_results_are_exhausted() -> None:
    judge = ScriptedJudge([])
    request = make_request()

    with pytest.raises(NoScriptedJudgeResultError):
        judge.judge(request)

    assert judge.requests == [request]
