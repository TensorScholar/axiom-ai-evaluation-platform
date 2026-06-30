from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.ci_gate import GateInputError, GateResult, gate_result_from_summary
from app.domain import Dataset, Project
from app.evaluations import EvaluationRunRecord, EvaluationRunSummary, EvaluationStatus
from app.persistence.sqlite import PersistenceConflictError, SQLiteStore
from app.regression import RegressionSuite


router = APIRouter()

_DEFAULT_STORE = SQLiteStore(Path(os.environ.get("AXIOM_SQLITE_PATH", ".axiom/axiom.db")))
_DEFAULT_STORE_INITIALIZED = False


def get_store() -> SQLiteStore:
    global _DEFAULT_STORE_INITIALIZED
    if not _DEFAULT_STORE_INITIALIZED:
        _DEFAULT_STORE.initialize()
        _DEFAULT_STORE_INITIALIZED = True
    return _DEFAULT_STORE


StoreDependency = Annotated[SQLiteStore, Depends(get_store)]


@router.post("/projects", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(project: Project, store: StoreDependency) -> Project:
    try:
        store.save_project(project)
    except PersistenceConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="project already exists") from exc
    return project


@router.get("/projects", response_model=list[Project])
def list_projects(store: StoreDependency) -> list[Project]:
    return store.list_projects()


@router.get("/projects/{project_id}", response_model=Project)
def get_project(project_id: str, store: StoreDependency) -> Project:
    project = store.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="project not found")
    return project


@router.post("/datasets", response_model=Dataset, status_code=status.HTTP_201_CREATED)
def create_dataset(dataset: Dataset, store: StoreDependency) -> Dataset:
    try:
        store.save_dataset(dataset)
    except PersistenceConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="dataset already exists") from exc
    return dataset


@router.get("/datasets", response_model=list[Dataset])
def list_datasets(store: StoreDependency) -> list[Dataset]:
    return store.list_datasets()


@router.get("/datasets/{dataset_id}", response_model=Dataset)
def get_dataset(dataset_id: str, store: StoreDependency) -> Dataset:
    dataset = store.get_dataset(dataset_id)
    if dataset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="dataset not found")
    return dataset


@router.post(
    "/evaluation-runs",
    response_model=EvaluationRunRecord,
    status_code=status.HTTP_201_CREATED,
)
def create_evaluation_run(run: EvaluationRunRecord, store: StoreDependency) -> EvaluationRunRecord:
    try:
        store.save_evaluation_run(run)
    except PersistenceConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="evaluation run already exists",
        ) from exc
    return run


@router.get("/evaluation-runs", response_model=list[EvaluationRunRecord])
def list_evaluation_runs(
    store: StoreDependency,
    project_id: str | None = None,
    dataset_id: str | None = None,
    status_filter: EvaluationStatus | None = Query(default=None, alias="status"),
) -> list[EvaluationRunRecord]:
    return store.query_evaluation_runs(
        project_id=project_id,
        dataset_id=dataset_id,
        status=status_filter,
    )


@router.get("/evaluation-runs/{run_id}", response_model=EvaluationRunRecord)
def get_evaluation_run(run_id: str, store: StoreDependency) -> EvaluationRunRecord:
    run = store.get_evaluation_run(run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="evaluation run not found")
    return run


@router.post(
    "/regression-suites",
    response_model=RegressionSuite,
    status_code=status.HTTP_201_CREATED,
)
def create_regression_suite(suite: RegressionSuite, store: StoreDependency) -> RegressionSuite:
    try:
        store.save_regression_suite(suite)
    except PersistenceConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="regression suite already exists",
        ) from exc
    return suite


@router.get("/regression-suites", response_model=list[RegressionSuite])
def list_regression_suites(store: StoreDependency) -> list[RegressionSuite]:
    return store.list_regression_suites()


@router.get("/regression-suites/{suite_id}", response_model=RegressionSuite)
def get_regression_suite(suite_id: str, store: StoreDependency) -> RegressionSuite:
    suite = store.get_regression_suite(suite_id)
    if suite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="regression suite not found")
    return suite


@router.post("/gate-results/from-summary", response_model=GateResult)
def create_gate_result_from_summary(
    summary: EvaluationRunSummary,
    min_pass_rate: float = 1.0,
    max_error_rate: float = 0.0,
) -> GateResult:
    try:
        return gate_result_from_summary(
            summary,
            min_pass_rate=min_pass_rate,
            max_error_rate=max_error_rate,
        )
    except GateInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
