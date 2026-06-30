from __future__ import annotations

from typing import Any

from app.domain import DatasetId, EvaluationRunId, TestCase, TestCaseId
from app.regression.models import RegressionCase, RegressionRerunPlan, RegressionSuite


def failure_to_regression_case(
    *,
    regression_case_id: str,
    source_run_id: EvaluationRunId,
    test_case_id: TestCaseId,
    dataset_id: DatasetId,
    name: str,
    inputs: dict[str, Any],
    failure_reason: str,
    expected_output: str | None = None,
) -> RegressionCase:
    return RegressionCase(
        id=regression_case_id,
        source_run_id=source_run_id,
        test_case=TestCase(
            id=test_case_id,
            dataset_id=dataset_id,
            name=name,
            inputs=inputs,
            expected_output=expected_output,
        ),
        failure_reason=failure_reason,
    )


def build_regression_suite(
    *,
    suite_id: str,
    name: str,
    cases: list[RegressionCase],
) -> RegressionSuite:
    return RegressionSuite(id=suite_id, name=name, cases=cases)


def plan_regression_rerun(
    suite: RegressionSuite,
    *,
    model_name: str,
    prompt_version: str,
) -> RegressionRerunPlan:
    return RegressionRerunPlan(
        suite_id=suite.id,
        model_name=model_name,
        prompt_version=prompt_version,
        case_ids=[case.id for case in suite.cases],
    )
