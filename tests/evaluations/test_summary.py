import pytest
from pydantic import ValidationError

from app.evaluations import (
    EvaluationRunMetadata,
    EvaluationRunRecord,
    EvaluationRunSummary,
    EvaluationStatus,
    SampleOutcome,
    SampleResult,
    summarize_evaluation_run,
)


def make_metadata() -> EvaluationRunMetadata:
    return EvaluationRunMetadata(
        spec_version="spec-012",
        code_version="summary-test",
        dataset_fingerprint="dataset-fp",
        seed=0,
        parameters={},
    )


def test_evaluation_run_summary_validates_and_dumps_deterministically() -> None:
    summary = EvaluationRunSummary(
        run_id="run-1",
        status=EvaluationStatus.COMPLETED,
        total_samples=2,
        succeeded_samples=1,
        errored_samples=1,
        metric_count=2,
        passed_metrics=1,
        failed_metrics=1,
        pass_rate=0.5,
        error_rate=0.5,
    )

    assert summary.model_dump(mode="json") == {
        "run_id": "run-1",
        "status": "completed",
        "total_samples": 2,
        "succeeded_samples": 1,
        "errored_samples": 1,
        "metric_count": 2,
        "passed_metrics": 1,
        "failed_metrics": 1,
        "pass_rate": 0.5,
        "error_rate": 0.5,
    }

    with pytest.raises(ValidationError):
        EvaluationRunSummary(
            run_id="run-1",
            status=EvaluationStatus.COMPLETED,
            total_samples=-1,
            succeeded_samples=0,
            errored_samples=0,
            metric_count=0,
            passed_metrics=0,
            failed_metrics=0,
            pass_rate=0.0,
            error_rate=0.0,
        )

    with pytest.raises(ValidationError):
        EvaluationRunSummary(
            run_id="run-1",
            status=EvaluationStatus.COMPLETED,
            total_samples=1,
            succeeded_samples=1,
            errored_samples=0,
            metric_count=1,
            passed_metrics=1,
            failed_metrics=0,
            pass_rate=1.5,
            error_rate=0.0,
        )


def test_summarize_evaluation_run_counts_samples_metrics_and_rates() -> None:
    run = EvaluationRunRecord(
        id="run-1",
        project_id="project-1",
        dataset_id="dataset-1",
        status=EvaluationStatus.COMPLETED,
        metadata=make_metadata(),
        sample_results=[
            SampleResult(
                test_case_id="case-1",
                outcome=SampleOutcome.SUCCEEDED,
                output="ok",
                metadata={
                    "metrics": [
                        {"name": "exact_match", "passed": True, "score": 1.0},
                        {"name": "regex_match", "passed": False, "score": 0.0},
                    ]
                },
            ),
            SampleResult(
                test_case_id="case-2",
                outcome=SampleOutcome.ERRORED,
                error_message="provider failed",
                metadata={"metrics": [{"name": "ignored", "passed": True}]},
            ),
        ],
    )

    summary = summarize_evaluation_run(run)

    assert summary.model_dump(mode="json") == {
        "run_id": "run-1",
        "status": "completed",
        "total_samples": 2,
        "succeeded_samples": 1,
        "errored_samples": 1,
        "metric_count": 3,
        "passed_metrics": 2,
        "failed_metrics": 1,
        "pass_rate": pytest.approx(2 / 3),
        "error_rate": 0.5,
    }


def test_summarize_evaluation_run_uses_zero_rates_for_empty_runs() -> None:
    run = EvaluationRunRecord(
        id="run-1",
        project_id="project-1",
        dataset_id="dataset-1",
        status=EvaluationStatus.PENDING,
        metadata=make_metadata(),
        sample_results=[],
    )

    summary = summarize_evaluation_run(run)

    assert summary.total_samples == 0
    assert summary.metric_count == 0
    assert summary.pass_rate == 0.0
    assert summary.error_rate == 0.0
