import pytest

from app.domain import Dataset, Project, TestCase as DomainTestCase
from app.evaluations import EvaluationRunMetadata, EvaluationRunRecord, EvaluationStatus, SampleOutcome, SampleResult
from app.persistence.sqlite import PersistenceConflictError, SQLiteStore
from app.regression import build_regression_suite, failure_to_regression_case


def make_store(tmp_path) -> SQLiteStore:
    store = SQLiteStore(tmp_path / "axiom.db")
    store.initialize()
    return store


def test_sqlite_store_saves_loads_and_lists_projects(tmp_path) -> None:
    store = make_store(tmp_path)
    project = Project(id="project-1", name="AXIOM")
    later = Project(id="project-2", name="Later")

    store.save_project(later)
    store.save_project(project)

    assert store.get_project("project-1") == project
    assert store.get_project("missing") is None
    assert [item.id for item in store.list_projects()] == ["project-1", "project-2"]

    with pytest.raises(PersistenceConflictError):
        store.save_project(project)


def test_sqlite_store_saves_loads_and_lists_datasets(tmp_path) -> None:
    store = make_store(tmp_path)
    dataset = Dataset(id="dataset-1", project_id="project-1", name="Smoke")

    store.save_dataset(dataset)

    assert store.get_dataset("dataset-1") == dataset
    assert store.list_datasets() == [dataset]


def test_sqlite_store_saves_loads_and_lists_test_cases(tmp_path) -> None:
    store = make_store(tmp_path)
    test_case = DomainTestCase(
        id="case-1",
        dataset_id="dataset-1",
        name="Health",
        inputs={"prompt": "Say ok"},
        expected_output="ok",
    )

    store.save_test_case(test_case)

    assert store.get_test_case("case-1") == test_case
    assert store.list_test_cases() == [test_case]


def test_sqlite_store_saves_loads_and_lists_evaluation_runs(tmp_path) -> None:
    store = make_store(tmp_path)
    run = EvaluationRunRecord(
        id="run-1",
        project_id="project-1",
        dataset_id="dataset-1",
        status=EvaluationStatus.COMPLETED,
        metadata=EvaluationRunMetadata(
            spec_version="spec",
            code_version="code",
            dataset_fingerprint="fingerprint",
            seed=0,
            parameters={},
        ),
        sample_results=[
            SampleResult(
                test_case_id="case-1",
                outcome=SampleOutcome.SUCCEEDED,
                output="ok",
                metadata={"metrics": []},
            )
        ],
    )

    store.save_evaluation_run(run)

    assert store.get_evaluation_run("run-1") == run
    assert store.list_evaluation_runs() == [run]


def test_sqlite_store_saves_loads_and_lists_regression_suites(tmp_path) -> None:
    store = make_store(tmp_path)
    case = failure_to_regression_case(
        regression_case_id="regression-1",
        source_run_id="run-1",
        test_case_id="case-1",
        dataset_id="dataset-1",
        name="Failure",
        inputs={"prompt": "Say ok"},
        failure_reason="wrong output",
        expected_output="ok",
    )
    suite = build_regression_suite(suite_id="suite-1", name="Failures", cases=[case])

    store.save_regression_suite(suite)

    assert store.get_regression_suite("suite-1") == suite
    assert store.list_regression_suites() == [suite]
