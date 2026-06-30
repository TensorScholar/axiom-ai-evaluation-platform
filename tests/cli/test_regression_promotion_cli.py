import json
from io import StringIO

from app.cli import main
from app.domain import TestCase as DomainTestCase
from app.evaluations import (
    EvaluationRunMetadata,
    EvaluationRunRecord,
    EvaluationStatus,
    SampleOutcome,
    SampleResult,
)


def make_metadata() -> EvaluationRunMetadata:
    return EvaluationRunMetadata(
        spec_version="spec-051",
        code_version="promotion-cli-test",
        dataset_fingerprint="dataset-fp",
        seed=0,
        parameters={},
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


def test_promote_regressions_cli_writes_promotion_result(tmp_path) -> None:
    run_file = tmp_path / "run.json"
    test_cases_file = tmp_path / "test_cases.json"
    output_file = tmp_path / "promotion.json"
    run_file.write_text(json.dumps(make_run().model_dump(mode="json")), encoding="utf-8")
    test_cases_file.write_text(
        json.dumps([case.model_dump(mode="json") for case in make_test_cases()]),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "promote-regressions",
            "--run-file",
            str(run_file),
            "--test-cases-file",
            str(test_cases_file),
            "--output-file",
            str(output_file),
            "--suite-id",
            "suite-051",
            "--suite-name",
            "Promoted failures",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert stdout.getvalue() == "AXIOM regression promotion completed: 2 cases promoted to suite-051\n"
    assert stderr.getvalue() == ""
    assert payload["promoted_count"] == 2
    assert payload["skipped_duplicate_count"] == 1


def test_promote_regressions_cli_returns_two_for_invalid_run(tmp_path) -> None:
    run_file = tmp_path / "run.json"
    test_cases_file = tmp_path / "test_cases.json"
    output_file = tmp_path / "promotion.json"
    run_file.write_text(json.dumps({"id": " "}), encoding="utf-8")
    test_cases_file.write_text(
        json.dumps([case.model_dump(mode="json") for case in make_test_cases()]),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "promote-regressions",
            "--run-file",
            str(run_file),
            "--test-cases-file",
            str(test_cases_file),
            "--output-file",
            str(output_file),
            "--suite-id",
            "suite-051",
            "--suite-name",
            "Promoted failures",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert stderr.getvalue().startswith("AXIOM promote-regressions error:")
