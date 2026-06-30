import json

import pytest

from app.domain import TestCase as DomainTestCase
from app.evaluations import (
    EvaluationRunMetadata,
    EvaluationRunRecord,
    EvaluationStatus,
    SampleOutcome,
    SampleResult,
)
from app.regression import (
    RegressionPromotionError,
    promote_failed_samples_to_regression_suite,
    run_regression_promotion_from_files,
)


def make_metadata() -> EvaluationRunMetadata:
    return EvaluationRunMetadata(
        spec_version="spec-051",
        code_version="promotion-test",
        dataset_fingerprint="dataset-fp",
        seed=7,
        parameters={"prompt_version": "prompt-v1"},
    )


def make_run() -> EvaluationRunRecord:
    return EvaluationRunRecord(
        id="run-051",
        project_id="project-1",
        dataset_id="dataset-1",
        status=EvaluationStatus.COMPLETED,
        metadata=make_metadata(),
        sample_results=[
            SampleResult(
                test_case_id="case-ok",
                outcome=SampleOutcome.SUCCEEDED,
                output="ok",
                metadata={"metrics": [{"name": "exact_match", "passed": True}]},
            ),
            SampleResult(
                test_case_id="case-metric",
                outcome=SampleOutcome.SUCCEEDED,
                output="bad",
                metadata={"metrics": [{"name": "exact_match", "passed": False}]},
            ),
            SampleResult(
                test_case_id="case-error",
                outcome=SampleOutcome.ERRORED,
                error_message="provider failed",
            ),
            SampleResult(
                test_case_id="case-error",
                outcome=SampleOutcome.ERRORED,
                error_message="provider failed again",
            ),
        ],
    )


def make_test_cases() -> list[DomainTestCase]:
    return [
        DomainTestCase(
            id="case-ok",
            dataset_id="dataset-1",
            name="Passing case",
            inputs={"prompt": "ok"},
            expected_output="ok",
        ),
        DomainTestCase(
            id="case-metric",
            dataset_id="dataset-1",
            name="Metric failure",
            inputs={"prompt": "bad"},
            expected_output="good",
        ),
        DomainTestCase(
            id="case-error",
            dataset_id="dataset-1",
            name="Provider error",
            inputs={"prompt": "fail"},
        ),
    ]


def test_promote_failed_samples_deduplicates_and_preserves_source_metadata() -> None:
    result = promote_failed_samples_to_regression_suite(
        run=make_run(),
        test_cases=make_test_cases(),
        suite_id="suite-051",
        suite_name="Promoted failures",
    )

    assert result.model_dump(mode="json") == {
        "dataset_id": "dataset-1",
        "project_id": "project-1",
        "promoted_count": 2,
        "skipped_duplicate_count": 1,
        "source_metadata": {
            "code_version": "promotion-test",
            "dataset_fingerprint": "dataset-fp",
            "parameters": {"prompt_version": "prompt-v1"},
            "seed": 7,
            "spec_version": "spec-051",
        },
        "source_run_id": "run-051",
        "suite": {
            "cases": [
                {
                    "failure_reason": "metric exact_match failed",
                    "id": "regression-run-051-case-metric",
                    "source_run_id": "run-051",
                    "test_case": {
                        "dataset_id": "dataset-1",
                        "expected_output": "good",
                        "id": "case-metric",
                        "inputs": {"prompt": "bad"},
                        "name": "Metric failure",
                    },
                },
                {
                    "failure_reason": "provider failed",
                    "id": "regression-run-051-case-error",
                    "source_run_id": "run-051",
                    "test_case": {
                        "dataset_id": "dataset-1",
                        "expected_output": None,
                        "id": "case-error",
                        "inputs": {"prompt": "fail"},
                        "name": "Provider error",
                    },
                },
            ],
            "id": "suite-051",
            "name": "Promoted failures",
        },
    }


def test_promote_failed_samples_rejects_missing_test_case_for_failed_sample() -> None:
    with pytest.raises(RegressionPromotionError, match="missing test case"):
        promote_failed_samples_to_regression_suite(
            run=make_run(),
            test_cases=make_test_cases()[:1],
            suite_id="suite-051",
            suite_name="Promoted failures",
        )


def test_promote_failed_samples_rejects_runs_without_failures() -> None:
    run = EvaluationRunRecord(
        id="run-ok",
        project_id="project-1",
        dataset_id="dataset-1",
        status=EvaluationStatus.COMPLETED,
        metadata=make_metadata(),
        sample_results=[
            SampleResult(test_case_id="case-ok", outcome=SampleOutcome.SUCCEEDED, output="ok")
        ],
    )

    with pytest.raises(RegressionPromotionError, match="no failed samples"):
        promote_failed_samples_to_regression_suite(
            run=run,
            test_cases=make_test_cases(),
            suite_id="suite-051",
            suite_name="Promoted failures",
        )


def test_run_regression_promotion_from_files_writes_reviewable_json(tmp_path) -> None:
    run_file = tmp_path / "run.json"
    test_cases_file = tmp_path / "test_cases.json"
    output_file = tmp_path / "promotion.json"
    run_file.write_text(json.dumps(make_run().model_dump(mode="json")), encoding="utf-8")
    test_cases_file.write_text(
        json.dumps({"test_cases": [case.model_dump(mode="json") for case in make_test_cases()]}),
        encoding="utf-8",
    )

    result = run_regression_promotion_from_files(
        run_file=run_file,
        test_cases_file=test_cases_file,
        output_file=output_file,
        suite_id="suite-051",
        suite_name="Promoted failures",
    )

    payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert result.promoted_count == 2
    assert payload["source_run_id"] == "run-051"
    assert payload["suite"]["cases"][0]["id"] == "regression-run-051-case-metric"
