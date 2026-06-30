from app.evaluations import EvaluationRunMetadata, EvaluationRunRecord, EvaluationStatus, SampleOutcome, SampleResult
from app.persistence import SQLiteStore


def make_store(tmp_path) -> SQLiteStore:
    store = SQLiteStore(tmp_path / "axiom.db")
    store.initialize()
    return store


def metadata() -> EvaluationRunMetadata:
    return EvaluationRunMetadata(
        spec_version="spec",
        code_version="code",
        dataset_fingerprint="fingerprint",
        seed=0,
        parameters={},
    )


def make_run(run_id: str, project_id: str, dataset_id: str, status: EvaluationStatus, samples: list[SampleResult]):
    return EvaluationRunRecord(
        id=run_id,
        project_id=project_id,
        dataset_id=dataset_id,
        status=status,
        metadata=metadata(),
        sample_results=samples,
    )


def test_query_evaluation_runs_filters_by_project_dataset_and_status(tmp_path) -> None:
    store = make_store(tmp_path)
    run_a = make_run("run-a", "project-1", "dataset-1", EvaluationStatus.COMPLETED, [])
    run_b = make_run("run-b", "project-1", "dataset-2", EvaluationStatus.FAILED, [])
    run_c = make_run("run-c", "project-2", "dataset-1", EvaluationStatus.COMPLETED, [])
    for run in [run_c, run_b, run_a]:
        store.save_evaluation_run(run)

    assert [run.id for run in store.query_evaluation_runs(project_id="project-1")] == ["run-a", "run-b"]
    assert [run.id for run in store.query_evaluation_runs(dataset_id="dataset-1")] == ["run-a", "run-c"]
    assert [run.id for run in store.query_evaluation_runs(status=EvaluationStatus.COMPLETED)] == ["run-a", "run-c"]
    assert store.query_evaluation_runs(project_id="missing") == []


def test_list_failed_samples_includes_errored_and_failed_metric_samples(tmp_path) -> None:
    store = make_store(tmp_path)
    run = make_run(
        "run-1",
        "project-1",
        "dataset-1",
        EvaluationStatus.COMPLETED,
        [
            SampleResult(test_case_id="case-ok", outcome=SampleOutcome.SUCCEEDED, output="ok", metadata={"metrics": [{"name": "exact_match", "passed": True}]}),
            SampleResult(test_case_id="case-metric", outcome=SampleOutcome.SUCCEEDED, output="bad", metadata={"metrics": [{"name": "exact_match", "passed": False}]}),
            SampleResult(test_case_id="case-error", outcome=SampleOutcome.ERRORED, error_message="provider failed"),
        ],
    )
    store.save_evaluation_run(run)

    failures = store.list_failed_samples(project_id="project-1")

    assert [failure.model_dump(mode="json") for failure in failures] == [
        {
            "run_id": "run-1",
            "test_case_id": "case-metric",
            "outcome": "succeeded",
            "output": "bad",
            "error_message": None,
            "reason": "failed metrics: exact_match",
        },
        {
            "run_id": "run-1",
            "test_case_id": "case-error",
            "outcome": "errored",
            "output": None,
            "error_message": "provider failed",
            "reason": "provider failed",
        },
    ]


def test_list_regression_candidates_are_derived_from_failed_samples(tmp_path) -> None:
    store = make_store(tmp_path)
    run = make_run(
        "run-1",
        "project-1",
        "dataset-1",
        EvaluationStatus.COMPLETED,
        [SampleResult(test_case_id="case-1", outcome=SampleOutcome.ERRORED, error_message="tool failed")],
    )
    store.save_evaluation_run(run)

    candidates = store.list_regression_candidates(dataset_id="dataset-1")

    assert [candidate.model_dump(mode="json") for candidate in candidates] == [
        {"run_id": "run-1", "test_case_id": "case-1", "failure_reason": "tool failed"}
    ]
    assert store.list_regression_candidates(dataset_id="missing") == []
