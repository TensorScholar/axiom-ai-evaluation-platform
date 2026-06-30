import pytest

from app.domain import TestCase as DomainTestCase
from app.evaluations import (
    EvaluationRunMetadata,
    EvaluationStatus,
    SampleOutcome,
    build_prompt,
    run_evaluation_cases,
)
from app.providers import FakeProvider, ProviderResponse


def make_metadata() -> EvaluationRunMetadata:
    return EvaluationRunMetadata(
        spec_version="spec-010",
        code_version="runner-test",
        dataset_fingerprint="dataset-fp",
        seed=0,
        parameters={},
    )


def test_build_prompt_prefers_prompt_input() -> None:
    assert build_prompt({"prompt": "Use this directly", "ignored": True}) == "Use this directly"


def test_build_prompt_uses_sorted_json_for_structured_inputs() -> None:
    assert build_prompt({"b": 2, "a": 1}) == '{"a":1,"b":2}'


def test_run_evaluation_cases_records_successful_samples_and_metric_metadata() -> None:
    test_cases = [
        DomainTestCase(
            id="case-1",
            dataset_id="dataset-1",
            name="Direct prompt",
            inputs={"prompt": "Say ok"},
            expected_output="ok",
        ),
        DomainTestCase(
            id="case-2",
            dataset_id="dataset-1",
            name="Structured prompt",
            inputs={"question": "What is 6 * 7?"},
            expected_output="42",
        ),
    ]
    provider = FakeProvider(
        [
            ProviderResponse(text="ok", model_name="fake-model", metadata={"tokens": 1}),
            ProviderResponse(text="41", model_name="fake-model", metadata={"tokens": 2}),
        ]
    )

    run = run_evaluation_cases(
        run_id="run-010",
        project_id="project-1",
        dataset_id="dataset-1",
        test_cases=test_cases,
        provider=provider,
        model_name="fake-model",
        metadata=make_metadata(),
        provider_parameters={"temperature": 0},
    )

    assert run.status == EvaluationStatus.COMPLETED
    assert [request.prompt for request in provider.requests] == [
        "Say ok",
        '{"question":"What is 6 * 7?"}',
    ]
    assert [request.parameters for request in provider.requests] == [
        {"temperature": 0},
        {"temperature": 0},
    ]
    assert [sample.outcome for sample in run.sample_results] == [
        SampleOutcome.SUCCEEDED,
        SampleOutcome.SUCCEEDED,
    ]
    assert run.sample_results[0].metadata["metrics"] == [
        {
            "name": "exact_match",
            "passed": True,
            "score": 1.0,
            "details": {"actual": "ok", "expected": "ok"},
        }
    ]
    assert run.sample_results[1].metadata["metrics"] == [
        {
            "name": "exact_match",
            "passed": False,
            "score": 0.0,
            "details": {"actual": "41", "expected": "42"},
        }
    ]


def test_run_evaluation_cases_records_provider_exceptions_as_sample_errors() -> None:
    test_case = DomainTestCase(
        id="case-1",
        dataset_id="dataset-1",
        name="No scripted response",
        inputs={"prompt": "fail"},
    )
    provider = FakeProvider(echo_fallback=False)

    run = run_evaluation_cases(
        run_id="run-010",
        project_id="project-1",
        dataset_id="dataset-1",
        test_cases=[test_case],
        provider=provider,
        model_name="fake-model",
        metadata=make_metadata(),
    )

    assert run.status == EvaluationStatus.COMPLETED
    assert run.sample_results[0].outcome == SampleOutcome.ERRORED
    assert run.sample_results[0].error_message == "fake provider has no scripted responses remaining"
    assert run.sample_results[0].metadata == {
        "prompt": "fail",
        "exception_type": "NoScriptedResponseError",
    }


def test_run_evaluation_cases_rejects_empty_test_case_lists() -> None:
    with pytest.raises(ValueError, match="at least one test case is required"):
        run_evaluation_cases(
            run_id="run-010",
            project_id="project-1",
            dataset_id="dataset-1",
            test_cases=[],
            provider=FakeProvider(),
            model_name="fake-model",
            metadata=make_metadata(),
        )
