from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy import Column, MetaData, String, Table, Text, create_engine, insert, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

from app.domain import Dataset, Project, TestCase
from app.evaluations import EvaluationRunRecord, EvaluationStatus, SampleOutcome
from app.persistence.query_models import FailedSampleRecord, RegressionCandidate
from app.regression import RegressionSuite


class PersistenceConflictError(ValueError):
    pass


class SQLiteStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.engine = create_engine(f"sqlite:///{self.path}", future=True)
        self.metadata = MetaData()
        self.projects = Table(
            "projects",
            self.metadata,
            Column("id", String, primary_key=True),
            Column("name", String, nullable=False),
            Column("payload", Text, nullable=False),
        )
        self.datasets = Table(
            "datasets",
            self.metadata,
            Column("id", String, primary_key=True),
            Column("project_id", String, nullable=False),
            Column("name", String, nullable=False),
            Column("payload", Text, nullable=False),
        )
        self.test_cases = Table(
            "test_cases",
            self.metadata,
            Column("id", String, primary_key=True),
            Column("dataset_id", String, nullable=False),
            Column("payload", Text, nullable=False),
        )
        self.evaluation_runs = Table(
            "evaluation_runs",
            self.metadata,
            Column("id", String, primary_key=True),
            Column("project_id", String, nullable=False),
            Column("dataset_id", String, nullable=False),
            Column("status", String, nullable=False),
            Column("payload", Text, nullable=False),
        )
        self.regression_suites = Table(
            "regression_suites",
            self.metadata,
            Column("id", String, primary_key=True),
            Column("name", String, nullable=False),
            Column("payload", Text, nullable=False),
        )

    def initialize(self) -> None:
        self.metadata.create_all(self.engine)

    def save_project(self, project: Project) -> None:
        self._insert(
            self.projects,
            {"id": str(project.id), "name": project.name, "payload": _dump(project)},
        )

    def get_project(self, project_id: str) -> Project | None:
        return self._get_payload(self.projects, project_id, Project)

    def list_projects(self) -> list[Project]:
        return self._list_payloads(self.projects, Project)

    def save_dataset(self, dataset: Dataset) -> None:
        self._insert(
            self.datasets,
            {
                "id": str(dataset.id),
                "project_id": str(dataset.project_id),
                "name": dataset.name,
                "payload": _dump(dataset),
            },
        )

    def get_dataset(self, dataset_id: str) -> Dataset | None:
        return self._get_payload(self.datasets, dataset_id, Dataset)

    def list_datasets(self) -> list[Dataset]:
        return self._list_payloads(self.datasets, Dataset)

    def save_test_case(self, test_case: TestCase) -> None:
        self._insert(
            self.test_cases,
            {
                "id": str(test_case.id),
                "dataset_id": str(test_case.dataset_id),
                "payload": _dump(test_case),
            },
        )

    def get_test_case(self, test_case_id: str) -> TestCase | None:
        return self._get_payload(self.test_cases, test_case_id, TestCase)

    def list_test_cases(self) -> list[TestCase]:
        return self._list_payloads(self.test_cases, TestCase)

    def save_evaluation_run(self, run: EvaluationRunRecord) -> None:
        self._insert(
            self.evaluation_runs,
            {
                "id": str(run.id),
                "project_id": str(run.project_id),
                "dataset_id": str(run.dataset_id),
                "status": str(run.status.value if hasattr(run.status, "value") else run.status),
                "payload": _dump(run),
            },
        )

    def get_evaluation_run(self, run_id: str) -> EvaluationRunRecord | None:
        return self._get_payload(self.evaluation_runs, run_id, EvaluationRunRecord)

    def list_evaluation_runs(self) -> list[EvaluationRunRecord]:
        return self.query_evaluation_runs()

    def query_evaluation_runs(
        self,
        *,
        project_id: str | None = None,
        dataset_id: str | None = None,
        status: EvaluationStatus | str | None = None,
    ) -> list[EvaluationRunRecord]:
        statement = select(self.evaluation_runs.c.payload).order_by(self.evaluation_runs.c.id)
        if project_id is not None:
            statement = statement.where(self.evaluation_runs.c.project_id == project_id)
        if dataset_id is not None:
            statement = statement.where(self.evaluation_runs.c.dataset_id == dataset_id)
        if status is not None:
            status_value = status.value if isinstance(status, EvaluationStatus) else str(status)
            statement = statement.where(self.evaluation_runs.c.status == status_value)

        with self.engine.connect() as conn:
            rows = conn.execute(statement).all()
        return [EvaluationRunRecord.model_validate(json.loads(row.payload)) for row in rows]

    def list_failed_samples(
        self,
        *,
        project_id: str | None = None,
        dataset_id: str | None = None,
        status: EvaluationStatus | str | None = None,
    ) -> list[FailedSampleRecord]:
        failures: list[FailedSampleRecord] = []
        for run in self.query_evaluation_runs(project_id=project_id, dataset_id=dataset_id, status=status):
            for sample in run.sample_results:
                reason = _sample_failure_reason(sample)
                if reason is not None:
                    failures.append(
                        FailedSampleRecord(
                            run_id=run.id,
                            test_case_id=sample.test_case_id,
                            outcome=sample.outcome,
                            output=sample.output,
                            error_message=sample.error_message,
                            reason=reason,
                        )
                    )
        return failures

    def list_regression_candidates(
        self,
        *,
        project_id: str | None = None,
        dataset_id: str | None = None,
        status: EvaluationStatus | str | None = None,
    ) -> list[RegressionCandidate]:
        return [
            RegressionCandidate(
                run_id=failure.run_id,
                test_case_id=failure.test_case_id,
                failure_reason=failure.reason,
            )
            for failure in self.list_failed_samples(
                project_id=project_id,
                dataset_id=dataset_id,
                status=status,
            )
        ]

    def save_regression_suite(self, suite: RegressionSuite) -> None:
        self._insert(
            self.regression_suites,
            {"id": suite.id, "name": suite.name, "payload": _dump(suite)},
        )

    def get_regression_suite(self, suite_id: str) -> RegressionSuite | None:
        return self._get_payload(self.regression_suites, suite_id, RegressionSuite)

    def list_regression_suites(self) -> list[RegressionSuite]:
        return self._list_payloads(self.regression_suites, RegressionSuite)

    def _insert(self, table: Table, values: dict[str, Any]) -> None:
        try:
            with self.engine.begin() as conn:
                conn.execute(insert(table).values(**values))
        except IntegrityError as exc:
            raise PersistenceConflictError("record already exists") from exc

    def _get_payload(self, table: Table, record_id: str, model_type: type[Any]) -> Any | None:
        with self.engine.connect() as conn:
            row = conn.execute(select(table.c.payload).where(table.c.id == record_id)).first()
        if row is None:
            return None
        return model_type.model_validate(json.loads(row.payload))

    def _list_payloads(self, table: Table, model_type: type[Any]) -> list[Any]:
        with self.engine.connect() as conn:
            rows = conn.execute(select(table.c.payload).order_by(table.c.id)).all()
        return [model_type.model_validate(json.loads(row.payload)) for row in rows]


def _dump(model: Any) -> str:
    return json.dumps(model.model_dump(mode="json"), sort_keys=True)


def _sample_failure_reason(sample: Any) -> str | None:
    if sample.outcome == SampleOutcome.ERRORED:
        return sample.error_message or "sample errored"

    metrics = sample.metadata.get("metrics", [])
    if not isinstance(metrics, list):
        return None
    failed_names: list[str] = []
    for metric in metrics:
        if isinstance(metric, dict) and metric.get("passed") is False:
            name = metric.get("name")
            failed_names.append(str(name) if name else "unnamed metric")
    if failed_names:
        return "failed metrics: " + ", ".join(failed_names)
    return None
