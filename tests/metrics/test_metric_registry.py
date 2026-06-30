import pytest
from pydantic import ValidationError

from app.metrics import MetricSpec, evaluate_metric, evaluate_metrics


def test_metric_spec_validates_and_dumps_deterministically() -> None:
    spec = MetricSpec(name="regex_match", parameters={"pattern": "ok"})

    assert spec.model_dump(mode="json") == {
        "name": "regex_match",
        "parameters": {"pattern": "ok"},
    }

    with pytest.raises(ValidationError):
        MetricSpec(name=" ")


def test_registry_evaluates_exact_match() -> None:
    result = evaluate_metric(MetricSpec(name="exact_match"), actual="ok", expected="ok")

    assert result.passed
    assert result.score == 1.0

    with pytest.raises(ValueError, match="exact_match requires expected"):
        evaluate_metric(MetricSpec(name="exact_match"), actual="ok")


def test_registry_evaluates_regex_match() -> None:
    result = evaluate_metric(
        MetricSpec(name="regex_match", parameters={"pattern": r"ok$"}),
        actual="status ok",
    )

    assert result.passed

    with pytest.raises(ValueError, match="regex_match requires pattern"):
        evaluate_metric(MetricSpec(name="regex_match"), actual="ok")

    with pytest.raises(ValueError, match="regex_match requires string actual"):
        evaluate_metric(MetricSpec(name="regex_match", parameters={"pattern": "1"}), actual=1)


def test_registry_evaluates_numeric_tolerance() -> None:
    result = evaluate_metric(
        MetricSpec(name="numeric_tolerance", parameters={"tolerance": 0.25}),
        actual=10,
        expected=10.2,
    )

    assert result.passed

    with pytest.raises(ValueError, match="numeric_tolerance requires numeric expected"):
        evaluate_metric(
            MetricSpec(name="numeric_tolerance", parameters={"tolerance": 0.25}),
            actual=10,
            expected="10",
        )

    with pytest.raises(ValueError, match="numeric_tolerance requires numeric tolerance"):
        evaluate_metric(
            MetricSpec(name="numeric_tolerance", parameters={"tolerance": "0.25"}),
            actual=10,
            expected=10,
        )


def test_registry_evaluates_json_schema_match() -> None:
    result = evaluate_metric(
        MetricSpec(name="json_schema_match", parameters={"schema": {"type": "object"}}),
        actual={"ok": True},
    )

    assert result.passed

    with pytest.raises(ValueError, match="json_schema_match requires schema object"):
        evaluate_metric(MetricSpec(name="json_schema_match"), actual={"ok": True})


def test_registry_rejects_unknown_metrics() -> None:
    with pytest.raises(ValueError, match="unknown metric"):
        evaluate_metric(MetricSpec(name="semantic_similarity"), actual="ok")


def test_evaluate_metrics_preserves_order() -> None:
    results = evaluate_metrics(
        [
            MetricSpec(name="exact_match"),
            MetricSpec(name="regex_match", parameters={"pattern": "o"}),
        ],
        actual="ok",
        expected="ok",
    )

    assert [result.name for result in results] == ["exact_match", "regex_match"]
    assert [result.passed for result in results] == [True, True]
