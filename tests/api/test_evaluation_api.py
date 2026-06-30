from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api import get_store
from app.main import app
from app.persistence.sqlite import SQLiteStore


@pytest.fixture()
def client(tmp_path) -> Iterator[TestClient]:
    store = SQLiteStore(tmp_path / "axiom.db")
    store.initialize()

    def override_store() -> SQLiteStore:
        return store

    app.dependency_overrides[get_store] = override_store
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def project_payload(project_id: str = "project-1") -> dict[str, str]:
    return {"id": project_id, "name": "AXIOM"}


def dataset_payload(dataset_id: str = "dataset-1") -> dict[str, str]:
    return {"id": dataset_id, "project_id": "project-1", "name": "Smoke"}


def run_payload(run_id: str = "run-1", status: str = "completed") -> dict[str, object]:
    return {
        "id": run_id,
        "project_id": "project-1",
        "dataset_id": "dataset-1",
        "status": status,
        "metadata": {
            "spec_version": "spec-060",
            "code_version": "api-test",
            "dataset_fingerprint": "dataset-fp",
            "seed": 0,
            "parameters": {},
        },
        "sample_results": [
            {
                "test_case_id": "case-1",
                "outcome": "succeeded",
                "output": "ok",
                "error_message": None,
                "metadata": {"metrics": []},
            }
        ],
    }


def test_project_endpoints_create_list_get_and_conflict(client: TestClient) -> None:
    response = client.post("/projects", json=project_payload())
    assert response.status_code == 201
    assert response.json() == project_payload()

    assert client.get("/projects").json() == [project_payload()]
    assert client.get("/projects/project-1").json() == project_payload()
    assert client.get("/projects/missing").status_code == 404

    conflict = client.post("/projects", json=project_payload())
    assert conflict.status_code == 409
    assert conflict.json() == {"detail": "project already exists"}


def test_dataset_endpoints_create_list_and_get(client: TestClient) -> None:
    response = client.post("/datasets", json=dataset_payload())
    assert response.status_code == 201
    assert response.json() == dataset_payload()

    assert client.get("/datasets").json() == [dataset_payload()]
    assert client.get("/datasets/dataset-1").json() == dataset_payload()
    assert client.get("/datasets/missing").status_code == 404


def test_evaluation_run_endpoints_create_list_get_and_filter(client: TestClient) -> None:
    first = run_payload("run-1", "completed")
    second = run_payload("run-2", "failed")

    assert client.post("/evaluation-runs", json=second).status_code == 201
    assert client.post("/evaluation-runs", json=first).status_code == 201

    listed = client.get("/evaluation-runs").json()
    assert [item["id"] for item in listed] == ["run-1", "run-2"]
    assert client.get("/evaluation-runs/run-1").json() == first
    assert client.get("/evaluation-runs/missing").status_code == 404

    filtered = client.get("/evaluation-runs", params={"status": "failed"}).json()
    assert [item["id"] for item in filtered] == ["run-2"]


def test_evaluation_run_endpoint_rejects_invalid_payload(client: TestClient) -> None:
    response = client.post("/evaluation-runs", json={"id": "run-1"})

    assert response.status_code == 422
