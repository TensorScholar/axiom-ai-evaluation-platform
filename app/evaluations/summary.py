from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.domain import EvaluationRunId
from app.evaluations.models import EvaluationRunRecord, EvaluationStatus, SampleOutcome


class EvaluationRunSummary(BaseModel):
    model_config = ConfigDict(frozen=True, use_enum_values=True)

    run_id: EvaluationRunId
    status: EvaluationStatus
    total_samples: int = Field(ge=0)
    succeeded_samples: int = Field(ge=0)
    errored_samples: int = Field(ge=0)
    metric_count: int = Field(ge=0)
    passed_metrics: int = Field(ge=0)
    failed_metrics: int = Field(ge=0)
    pass_rate: float = Field(ge=0.0, le=1.0)
    error_rate: float = Field(ge=0.0, le=1.0)


def summarize_evaluation_run(run: EvaluationRunRecord) -> EvaluationRunSummary:
    total_samples = len(run.sample_results)
    succeeded_samples = sum(1 for sample in run.sample_results if sample.outcome == SampleOutcome.SUCCEEDED)
    errored_samples = sum(1 for sample in run.sample_results if sample.outcome == SampleOutcome.ERRORED)

    passed_metrics = 0
    failed_metrics = 0
    for sample in run.sample_results:
        metrics = sample.metadata.get("metrics", [])
        if not isinstance(metrics, list):
            continue
        for metric in metrics:
            if not isinstance(metric, dict):
                continue
            if metric.get("passed") is True:
                passed_metrics += 1
            elif metric.get("passed") is False:
                failed_metrics += 1

    metric_count = passed_metrics + failed_metrics
    pass_rate = passed_metrics / metric_count if metric_count else 0.0
    error_rate = errored_samples / total_samples if total_samples else 0.0

    return EvaluationRunSummary(
        run_id=run.id,
        status=run.status,
        total_samples=total_samples,
        succeeded_samples=succeeded_samples,
        errored_samples=errored_samples,
        metric_count=metric_count,
        passed_metrics=passed_metrics,
        failed_metrics=failed_metrics,
        pass_rate=pass_rate,
        error_rate=error_rate,
    )
