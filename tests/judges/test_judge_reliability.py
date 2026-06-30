import pytest
from pydantic import ValidationError

from app.judges import (
    JudgeReliabilityReport,
    JudgeResult,
    JudgeVerdict,
    assess_judge_reliability,
    position_swap_consistent,
)


def make_result(
    verdict: JudgeVerdict,
    score: float,
    *,
    test_case_id: str = "case-1",
) -> JudgeResult:
    return JudgeResult(
        test_case_id=test_case_id,
        rubric_id="rubric-1",
        rubric_version="v1",
        verdict=verdict,
        score=score,
        rationale="Structured judge rationale.",
        criteria_scores={"correctness": score},
    )


def test_reliability_report_validates_and_dumps_deterministically() -> None:
    report = JudgeReliabilityReport(
        judge_count=2,
        majority_verdict=JudgeVerdict.PASSED,
        agreement_rate=1.0,
        mean_score=0.9,
        score_spread=0.1,
        confidence=0.9,
        uncertainty=0.1,
        position_swap_consistent=True,
        requires_human_review=False,
        review_reasons=[],
    )

    assert report.model_dump(mode="json") == {
        "judge_count": 2,
        "majority_verdict": "passed",
        "agreement_rate": 1.0,
        "mean_score": 0.9,
        "score_spread": 0.1,
        "confidence": 0.9,
        "uncertainty": 0.1,
        "position_swap_consistent": True,
        "requires_human_review": False,
        "review_reasons": [],
    }

    with pytest.raises(ValidationError):
        JudgeReliabilityReport(
            judge_count=1,
            majority_verdict=None,
            agreement_rate=0.5,
            mean_score=0.5,
            score_spread=0.0,
            confidence=0.5,
            uncertainty=0.5,
            requires_human_review=True,
            review_reasons=[" "],
        )


def test_position_swap_consistency_passes_and_fails() -> None:
    original = make_result(JudgeVerdict.PASSED, 0.9)
    close_swap = make_result(JudgeVerdict.PASSED, 0.8)
    different_verdict = make_result(JudgeVerdict.FAILED, 0.8)
    far_swap = make_result(JudgeVerdict.PASSED, 0.5)

    assert position_swap_consistent(original, close_swap, score_tolerance=0.15)
    assert not position_swap_consistent(original, different_verdict, score_tolerance=0.15)
    assert not position_swap_consistent(original, far_swap, score_tolerance=0.15)

    with pytest.raises(ValueError, match="score tolerance cannot be negative"):
        position_swap_consistent(original, close_swap, score_tolerance=-0.1)


def test_assess_judge_reliability_rejects_empty_results() -> None:
    with pytest.raises(ValueError, match="at least one judge result is required"):
        assess_judge_reliability([])


def test_assess_judge_reliability_calculates_agreement_and_confidence() -> None:
    results = [
        make_result(JudgeVerdict.PASSED, 0.9),
        make_result(JudgeVerdict.PASSED, 0.8),
        make_result(JudgeVerdict.FAILED, 0.4),
    ]

    report = assess_judge_reliability(results, confidence_threshold=0.5)

    assert report.majority_verdict == JudgeVerdict.PASSED
    assert report.agreement_rate == pytest.approx(2 / 3)
    assert report.mean_score == pytest.approx(0.7)
    assert report.score_spread == pytest.approx(0.5)
    assert report.confidence == pytest.approx((2 / 3) * 0.5)
    assert report.uncertainty == pytest.approx(1.0 - ((2 / 3) * 0.5))
    assert report.requires_human_review
    assert report.review_reasons == ["confidence below threshold"]


def test_assess_judge_reliability_flags_ties_and_position_swap_inconsistency() -> None:
    results = [
        make_result(JudgeVerdict.PASSED, 0.9),
        make_result(JudgeVerdict.FAILED, 0.9),
    ]
    swapped = make_result(JudgeVerdict.FAILED, 0.9)

    report = assess_judge_reliability(
        results,
        swapped_result=swapped,
        confidence_threshold=0.1,
    )

    assert report.majority_verdict is None
    assert report.agreement_rate == 0.5
    assert not report.position_swap_consistent
    assert report.requires_human_review
    assert report.review_reasons == [
        "no majority verdict",
        "position-swap inconsistency",
    ]


def test_assess_judge_reliability_can_pass_without_human_review() -> None:
    results = [
        make_result(JudgeVerdict.PASSED, 0.9),
        make_result(JudgeVerdict.PASSED, 0.85),
        make_result(JudgeVerdict.PASSED, 0.95),
    ]
    swapped = make_result(JudgeVerdict.PASSED, 0.87)

    report = assess_judge_reliability(results, swapped_result=swapped)

    assert report.model_dump(mode="json") == {
        "judge_count": 3,
        "majority_verdict": "passed",
        "agreement_rate": 1.0,
        "mean_score": 0.9,
        "score_spread": pytest.approx(0.1),
        "confidence": pytest.approx(0.9),
        "uncertainty": pytest.approx(0.1),
        "position_swap_consistent": True,
        "requires_human_review": False,
        "review_reasons": [],
    }
