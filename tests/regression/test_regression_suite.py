import pytest
from pydantic import ValidationError

from app.regression import (
    RegressionRerunPlan,
    RegressionSuite,
    build_regression_suite,
    failure_to_regression_case,
    plan_regression_rerun,
)


def make_case(case_id: str = "regression-1"):
    return failure_to_regression_case(
        regression_case_id=case_id,
        source_run_id="run-1",
        test_case_id="case-1",
        dataset_id="dataset-1",
        name="Previously failed prompt",
        inputs={"question": "What is 6 * 7?"},
        failure_reason="model returned an incorrect answer",
        expected_output="42",
    )


def test_failure_to_regression_case_dumps_deterministically() -> None:
    case = make_case()

    assert case.model_dump(mode="json") == {
        "id": "regression-1",
        "source_run_id": "run-1",
        "test_case": {
            "id": "case-1",
            "dataset_id": "dataset-1",
            "name": "Previously failed prompt",
            "inputs": {"question": "What is 6 * 7?"},
            "expected_output": "42",
        },
        "failure_reason": "model returned an incorrect answer",
    }


@pytest.mark.parametrize(
    "kwargs",
    [
        {"regression_case_id": " ", "failure_reason": "failed"},
        {"regression_case_id": "regression-1", "failure_reason": " "},
    ],
)
def test_failure_to_regression_case_rejects_blank_required_fields(kwargs: dict[str, str]) -> None:
    base = {
        "source_run_id": "run-1",
        "test_case_id": "case-1",
        "dataset_id": "dataset-1",
        "name": "Failed case",
        "inputs": {"x": 1},
    }
    base.update(kwargs)

    with pytest.raises(ValidationError):
        failure_to_regression_case(**base)


def test_regression_suite_requires_non_empty_unique_cases() -> None:
    first = make_case("regression-1")
    second = make_case("regression-2")

    suite = build_regression_suite(
        suite_id="suite-1",
        name="Known failures",
        cases=[first, second],
    )

    assert suite.model_dump(mode="json")["cases"][0]["id"] == "regression-1"

    with pytest.raises(ValidationError, match="cases cannot be empty"):
        RegressionSuite(id="suite-1", name="Known failures", cases=[])

    with pytest.raises(ValidationError, match="case ids must be unique"):
        RegressionSuite(id="suite-1", name="Known failures", cases=[first, first])


@pytest.mark.parametrize(
    "kwargs",
    [
        {"id": " ", "name": "Known failures"},
        {"id": "suite-1", "name": " "},
    ],
)
def test_regression_suite_rejects_blank_id_or_name(kwargs: dict[str, str]) -> None:
    with pytest.raises(ValidationError):
        RegressionSuite(cases=[make_case()], **kwargs)


def test_plan_regression_rerun_preserves_case_order() -> None:
    suite = build_regression_suite(
        suite_id="suite-1",
        name="Known failures",
        cases=[make_case("regression-1"), make_case("regression-2")],
    )

    plan = plan_regression_rerun(
        suite,
        model_name="fake-model-v2",
        prompt_version="prompt-v3",
    )

    assert plan.model_dump(mode="json") == {
        "suite_id": "suite-1",
        "model_name": "fake-model-v2",
        "prompt_version": "prompt-v3",
        "case_ids": ["regression-1", "regression-2"],
    }


def test_rerun_plan_rejects_blank_fields_and_empty_case_ids() -> None:
    with pytest.raises(ValidationError):
        RegressionRerunPlan(
            suite_id="suite-1",
            model_name=" ",
            prompt_version="prompt-v1",
            case_ids=["regression-1"],
        )

    with pytest.raises(ValidationError):
        RegressionRerunPlan(
            suite_id="suite-1",
            model_name="fake-model",
            prompt_version="prompt-v1",
            case_ids=[],
        )
