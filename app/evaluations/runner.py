from __future__ import annotations

import json
from collections.abc import Sequence

from pydantic import JsonValue

from app.domain import DatasetId, EvaluationRunId, ProjectId, TestCase
from app.evaluations.lifecycle import new_evaluation_run, record_sample_result, transition_run
from app.evaluations.models import (
    EvaluationRunMetadata,
    EvaluationRunRecord,
    EvaluationStatus,
    SampleOutcome,
    SampleResult,
)
from app.metrics import exact_match
from app.providers import ProviderAdapter, ProviderRequest, classify_provider_exception


def build_prompt(inputs: dict[str, object]) -> str:
    prompt = inputs.get("prompt")
    if isinstance(prompt, str):
        return prompt
    return json.dumps(inputs, sort_keys=True, separators=(",", ":"))


def run_evaluation_cases(
    *,
    run_id: EvaluationRunId,
    project_id: ProjectId,
    dataset_id: DatasetId,
    test_cases: Sequence[TestCase],
    provider: ProviderAdapter,
    model_name: str,
    metadata: EvaluationRunMetadata,
    provider_parameters: dict[str, JsonValue] | None = None,
) -> EvaluationRunRecord:
    if not test_cases:
        raise ValueError("at least one test case is required")

    run = new_evaluation_run(
        run_id=run_id,
        project_id=project_id,
        dataset_id=dataset_id,
        metadata=metadata,
    )
    run = transition_run(run, EvaluationStatus.RUNNING)

    parameters = provider_parameters or {}
    for test_case in test_cases:
        prompt = build_prompt(test_case.inputs)
        request = ProviderRequest(prompt=prompt, model_name=model_name, parameters=parameters)
        sample = _run_sample(test_case, request, provider)
        run = record_sample_result(run, sample)

    return transition_run(run, EvaluationStatus.COMPLETED)


def _run_sample(
    test_case: TestCase,
    request: ProviderRequest,
    provider: ProviderAdapter,
) -> SampleResult:
    try:
        response = provider.generate(request)
    except Exception as exc:
        failure = classify_provider_exception(exc, provider_name=request.model_name)
        return SampleResult(
            test_case_id=test_case.id,
            outcome=SampleOutcome.ERRORED,
            error_message=failure.message,
            metadata={
                "prompt": request.prompt,
                "exception_type": exc.__class__.__name__,
                "provider_failure": failure.model_dump(mode="json"),
            },
        )

    metric_results: list[JsonValue] = []
    if test_case.expected_output is not None:
        metric_results.append(
            exact_match(response.text, test_case.expected_output).model_dump(mode="json")
        )

    return SampleResult(
        test_case_id=test_case.id,
        outcome=SampleOutcome.SUCCEEDED,
        output=response.text,
        metadata={
            "prompt": request.prompt,
            "provider_metadata": response.metadata,
            "metrics": metric_results,
        },
    )
