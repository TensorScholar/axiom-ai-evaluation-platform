import pytest
from pydantic import ValidationError

from app.evaluations import (
    EvaluationRunMetadata,
    EvaluationStatus,
    SampleOutcome,
    SampleResult,
    can_transition,
    new_evaluation_run,
    record_sample_result,
    transition_run,
)


def make_metadata() -> EvaluationRunMetadata:
    return EvaluationRunMetadata(
        spec_version="spec-1",
        code_version="abc123",
        dataset_fingerprint="dataset-sha",
        seed=7,
        parameters={"temperature": 0, "tags": ["smoke", "deterministic"]},
    )


def make_run():
    return new_evaluation_run(
        run_id="run-1",
        project_id="project-1",
        dataset_id="dataset-1",
        metadata=make_metadata(),
    )


def test_new_evaluation_run_starts_pending_and_dumps_deterministically() -> None:
    run = make_run()

    assert run.status == EvaluationStatus.PENDING
    assert run.sample_results == []
    assert run.model_dump(mode="json") == {
        "id": "run-1",
        "project_id": "project-1",
        "dataset_id": "dataset-1",
        "status": "pending",
        "metadata": {
            "spec_version": "spec-1",
            "code_version": "abc123",
            "dataset_fingerprint": "dataset-sha",
            "seed": 7,
            "parameters": {"temperature": 0, "tags": ["smoke", "deterministic"]},
        },
        "sample_results": [],
    }


def test_allowed_transitions_are_enforced() -> None:
    assert can_transition(EvaluationStatus.PENDING, EvaluationStatus.RUNNING)
    assert can_transition(EvaluationStatus.RUNNING, EvaluationStatus.COMPLETED)
    assert can_transition(EvaluationStatus.RUNNING, EvaluationStatus.FAILED)
    assert not can_transition(EvaluationStatus.PENDING, EvaluationStatus.COMPLETED)
    assert not can_transition(EvaluationStatus.COMPLETED, EvaluationStatus.RUNNING)


def test_transition_run_returns_new_record_without_mutating_previous_record() -> None:
    pending = make_run()

    running = transition_run(pending, EvaluationStatus.RUNNING)
    completed = transition_run(running, EvaluationStatus.COMPLETED)

    assert pending.status == EvaluationStatus.PENDING
    assert running.status == EvaluationStatus.RUNNING
    assert completed.status == EvaluationStatus.COMPLETED


@pytest.mark.parametrize(
    "from_status,next_status",
    [
        (EvaluationStatus.PENDING, EvaluationStatus.COMPLETED),
        (EvaluationStatus.PENDING, EvaluationStatus.FAILED),
        (EvaluationStatus.COMPLETED, EvaluationStatus.RUNNING),
        (EvaluationStatus.FAILED, EvaluationStatus.RUNNING),
    ],
)
def test_invalid_transitions_are_rejected(
    from_status: EvaluationStatus,
    next_status: EvaluationStatus,
) -> None:
    run = make_run().model_copy(update={"status": from_status})

    with pytest.raises(ValueError):
        transition_run(run, next_status)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"spec_version": " ", "code_version": "abc123", "dataset_fingerprint": "dataset-sha", "seed": 0},
        {"spec_version": "spec-1", "code_version": " ", "dataset_fingerprint": "dataset-sha", "seed": 0},
        {"spec_version": "spec-1", "code_version": "abc123", "dataset_fingerprint": " ", "seed": 0},
        {"spec_version": "spec-1", "code_version": "abc123", "dataset_fingerprint": "dataset-sha", "seed": -1},
    ],
)
def test_metadata_rejects_invalid_reproducibility_fields(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        EvaluationRunMetadata(**kwargs)


def test_sample_result_records_successful_output() -> None:
    result = SampleResult(
        test_case_id="case-1",
        outcome=SampleOutcome.SUCCEEDED,
        output={"answer": "ok"},
        metadata={"latency_ms": 12},
    )

    assert result.model_dump(mode="json") == {
        "test_case_id": "case-1",
        "outcome": "succeeded",
        "output": {"answer": "ok"},
        "error_message": None,
        "metadata": {"latency_ms": 12},
    }


def test_sample_result_validates_error_fields() -> None:
    with pytest.raises(ValidationError):
        SampleResult(test_case_id="case-1", outcome=SampleOutcome.ERRORED, error_message=" ")

    with pytest.raises(ValidationError):
        SampleResult(
            test_case_id="case-1",
            outcome=SampleOutcome.SUCCEEDED,
            output="ok",
            error_message="should not be here",
        )


def test_record_sample_result_requires_running_run_and_preserves_previous_record() -> None:
    pending = make_run()
    running = transition_run(pending, EvaluationStatus.RUNNING)
    result = SampleResult(test_case_id="case-1", outcome=SampleOutcome.SUCCEEDED, output="ok")

    updated = record_sample_result(running, result)

    assert running.sample_results == []
    assert updated.sample_results == [result]

    with pytest.raises(ValueError):
        record_sample_result(pending, result)
