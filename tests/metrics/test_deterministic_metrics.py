import pytest
from pydantic import ValidationError

from app.metrics import (
    MetricResult,
    exact_match,
    json_schema_match,
    numeric_tolerance,
    regex_match,
)


def test_metric_result_validates_name_and_score() -> None:
    result = MetricResult(name="metric", passed=True, score=1.0, details={"x": 1})

    assert result.model_dump(mode="json") == {
        "name": "metric",
        "passed": True,
        "score": 1.0,
        "details": {"x": 1},
    }

    with pytest.raises(ValidationError):
        MetricResult(name=" ", passed=True, score=1.0)

    with pytest.raises(ValidationError):
        MetricResult(name="metric", passed=True, score=1.5)


def test_exact_match_passes_and_fails_deterministically() -> None:
    assert exact_match({"answer": "ok"}, {"answer": "ok"}).model_dump(mode="json") == {
        "name": "exact_match",
        "passed": True,
        "score": 1.0,
        "details": {"actual": {"answer": "ok"}, "expected": {"answer": "ok"}},
    }
    assert not exact_match("ok", "no").passed


def test_regex_match_passes_fails_and_rejects_invalid_patterns() -> None:
    assert regex_match("trace finished successfully", r"finished").passed
    assert not regex_match("trace failed", r"success$").passed

    with pytest.raises(ValueError, match="invalid regex pattern"):
        regex_match("value", "[")


def test_numeric_tolerance_passes_fails_and_rejects_invalid_tolerance() -> None:
    assert numeric_tolerance(10.0, 10.2, 0.25).passed
    assert not numeric_tolerance(10.0, 10.3, 0.25).passed

    with pytest.raises(ValueError, match="tolerance cannot be negative"):
        numeric_tolerance(10.0, 10.0, -0.1)


def test_json_schema_match_validates_supported_schema_subset() -> None:
    schema = {
        "type": "object",
        "required": ["answer", "scores"],
        "properties": {
            "answer": {"type": "string", "enum": ["yes", "no"]},
            "scores": {"type": "array", "items": {"type": "number"}},
            "stable": {"const": True},
        },
    }

    passed = json_schema_match(
        {"answer": "yes", "scores": [1, 0.5], "stable": True},
        schema,
    )
    failed = json_schema_match(
        {"answer": "maybe", "scores": [1, "bad"], "stable": False},
        schema,
    )

    assert passed.model_dump(mode="json") == {
        "name": "json_schema_match",
        "passed": True,
        "score": 1.0,
        "details": {"errors": []},
    }
    assert not failed.passed
    assert failed.score == 0.0
    assert failed.details["errors"] == [
        "$.answer: value is not in enum",
        "$.scores[1]: expected type number",
        "$.stable: expected const True",
    ]


def test_json_schema_match_reports_missing_required_properties() -> None:
    result = json_schema_match(
        {"answer": "yes"},
        {"type": "object", "required": ["answer", "reason"]},
    )

    assert not result.passed
    assert result.details == {"errors": ["$: missing required property reason"]}


def test_json_schema_match_rejects_unsupported_types() -> None:
    with pytest.raises(ValueError, match="unsupported schema type"):
        json_schema_match("value", {"type": "date"})
