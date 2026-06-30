from __future__ import annotations

from app.domain import DatasetId, EvaluationRunId, ProjectId
from app.evaluations.models import (
    EvaluationRunMetadata,
    EvaluationRunRecord,
    EvaluationStatus,
    SampleResult,
)

ALLOWED_TRANSITIONS: dict[EvaluationStatus, set[EvaluationStatus]] = {
    EvaluationStatus.PENDING: {EvaluationStatus.RUNNING},
    EvaluationStatus.RUNNING: {EvaluationStatus.COMPLETED, EvaluationStatus.FAILED},
    EvaluationStatus.COMPLETED: set(),
    EvaluationStatus.FAILED: set(),
}


def can_transition(current: EvaluationStatus, next_status: EvaluationStatus) -> bool:
    return next_status in ALLOWED_TRANSITIONS[current]


def transition_run(
    run: EvaluationRunRecord,
    next_status: EvaluationStatus,
) -> EvaluationRunRecord:
    if not can_transition(run.status, next_status):
        raise ValueError(f"cannot transition evaluation run from {run.status} to {next_status}")
    return run.model_copy(update={"status": next_status})


def new_evaluation_run(
    *,
    run_id: EvaluationRunId,
    project_id: ProjectId,
    dataset_id: DatasetId,
    metadata: EvaluationRunMetadata,
) -> EvaluationRunRecord:
    return EvaluationRunRecord(
        id=run_id,
        project_id=project_id,
        dataset_id=dataset_id,
        status=EvaluationStatus.PENDING,
        metadata=metadata,
        sample_results=[],
    )


def record_sample_result(
    run: EvaluationRunRecord,
    result: SampleResult,
) -> EvaluationRunRecord:
    if run.status != EvaluationStatus.RUNNING:
        raise ValueError("sample results can only be recorded while a run is running")
    return run.model_copy(update={"sample_results": [*run.sample_results, result]})
