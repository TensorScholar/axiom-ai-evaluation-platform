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


def regression_suite_payload(suite_id: str = "suite-1") -> dict[str, object]:
    return {
        "id": suite_id,
        "name": "Known failures",
        "cases": [
            {
                "id": "regression-1",
                "source_run_id": "run-1",
                "test_case": {
                    "id": "case-1",
                    "dataset_id": "dataset-1",
                    "name": "Failed prompt",
                    "inputs": {"prompt": "Say ok"},
                    "expected_output": "ok",
                },
                "failure_reason": "wrong output",
            }
        ],
    }


def summary_payload(**overrides: object) -> dict[str, object]:
    payload = {
        "run_id": "run-1",
        "status": "completed",
        "total_samples": 2,
        "succeeded_samples": 1,
        "errored_samples": 1,
        "metric_count": 2,
        "passed_metrics": 1,
        "failed_metrics": 1,
        "pass_rate": 0.5,
        "error_rate": 0.5,
    }
    payload.update(overrides)
    return payload


def test_regression_suite_endpoints_create_list_get_and_conflict(client: TestClient) -> None:
    suite = regression_suite_payload()

    response = client.post("/regression-suites", json=suite)
    assert response.status_code == 201
    assert response.json() == suite

    assert client.get("/regression-suites").json() == [suite]
    assert client.get("/regression-suites/suite-1").json() == suite
    assert client.get("/regression-suites/missing").status_code == 404

    conflict = client.post("/regression-suites", json=suite)
    assert conflict.status_code == 409
    assert conflict.json() == {"detail": "regression suite already exists"}


def test_regression_suite_endpoint_rejects_invalid_payload(client: TestClient) -> None:
    response = client.post("/regression-suites", json={"id": "suite-1", "name": "empty", "cases": []})

    assert response.status_code == 422


def test_gate_result_endpoint_derives_gate_result_from_summary(client: TestClient) -> None:
    response = client.post(
        "/gate-results/from-summary",
        params={"min_pass_rate": 0.75, "max_error_rate": 0.25},
        json=summary_payload(),
    )

    assert response.status_code == 200
    assert response.json() == {
        "suite_id": "run-1",
        "passed": False,
        "failures": [
            {
                "case_id": "run-1",
                "reason": "pass rate 0.5000 is below minimum 0.7500",
            },
            {
                "case_id": "run-1",
                "reason": "error rate 0.5000 exceeds maximum 0.2500",
            },
        ],
        "metrics": {
            "pass_rate": 0.5,
            "error_rate": 0.5,
            "total_samples": 2,
            "metric_count": 2,
        },
    }


def test_gate_result_endpoint_rejects_invalid_thresholds(client: TestClient) -> None:
    response = client.post(
        "/gate-results/from-summary",
        params={"min_pass_rate": 1.5},
        json=summary_payload(),
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "min_pass_rate must be between 0.0 and 1.0"}
