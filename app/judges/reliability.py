from __future__ import annotations

from collections import Counter

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.judges.models import JudgeResult, JudgeVerdict


class JudgeReliabilityReport(BaseModel):
    model_config = ConfigDict(frozen=True, use_enum_values=True)

    judge_count: int = Field(ge=1)
    majority_verdict: JudgeVerdict | None
    agreement_rate: float = Field(ge=0.0, le=1.0)
    mean_score: float = Field(ge=0.0, le=1.0)
    score_spread: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    uncertainty: float = Field(ge=0.0, le=1.0)
    position_swap_consistent: bool | None = None
    requires_human_review: bool
    review_reasons: list[str] = Field(default_factory=list)

    @field_validator("review_reasons")
    @classmethod
    def review_reasons_must_not_be_blank(cls, value: list[str]) -> list[str]:
        for reason in value:
            if not reason.strip():
                raise ValueError("review reasons cannot be blank")
        return value


def position_swap_consistent(
    original: JudgeResult,
    swapped: JudgeResult,
    *,
    score_tolerance: float = 0.15,
) -> bool:
    if score_tolerance < 0:
        raise ValueError("score tolerance cannot be negative")
    return original.verdict == swapped.verdict and abs(original.score - swapped.score) <= score_tolerance


def assess_judge_reliability(
    results: list[JudgeResult],
    *,
    swapped_result: JudgeResult | None = None,
    score_tolerance: float = 0.15,
    confidence_threshold: float = 0.75,
) -> JudgeReliabilityReport:
    if not results:
        raise ValueError("at least one judge result is required")
    if score_tolerance < 0:
        raise ValueError("score tolerance cannot be negative")
    if confidence_threshold < 0.0 or confidence_threshold > 1.0:
        raise ValueError("confidence threshold must be between 0.0 and 1.0")

    verdicts = [result.verdict for result in results]
    counts = Counter(verdicts)
    most_common = counts.most_common()
    majority_verdict = most_common[0][0]
    majority_count = most_common[0][1]
    if len(most_common) > 1 and most_common[0][1] == most_common[1][1]:
        majority_verdict = None

    agreement_rate = majority_count / len(results)
    scores = [result.score for result in results]
    mean_score = sum(scores) / len(scores)
    score_spread = max(scores) - min(scores)
    confidence = max(0.0, min(1.0, agreement_rate * (1.0 - score_spread)))
    uncertainty = 1.0 - confidence

    review_reasons: list[str] = []
    if majority_verdict is None:
        review_reasons.append("no majority verdict")
    if confidence < confidence_threshold:
        review_reasons.append("confidence below threshold")

    swap_consistent: bool | None = None
    if swapped_result is not None:
        swap_consistent = position_swap_consistent(
            results[0],
            swapped_result,
            score_tolerance=score_tolerance,
        )
        if not swap_consistent:
            review_reasons.append("position-swap inconsistency")

    return JudgeReliabilityReport(
        judge_count=len(results),
        majority_verdict=majority_verdict,
        agreement_rate=agreement_rate,
        mean_score=mean_score,
        score_spread=score_spread,
        confidence=confidence,
        uncertainty=uncertainty,
        position_swap_consistent=swap_consistent,
        requires_human_review=bool(review_reasons),
        review_reasons=review_reasons,
    )
