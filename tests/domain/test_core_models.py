import pytest
from pydantic import ValidationError

from app.domain import (
    Dataset,
    DatasetId,
    EvaluationRunId,
    EvaluationRunReference,
    Project,
    ProjectId,
    Rubric,
    RubricId,
    TestCase as DomainTestCase,
    TestCaseId as DomainTestCaseId,
)


def test_identifiers_preserve_valid_values() -> None:
    project_id = ProjectId("project-1")

    assert str(project_id) == "project-1"
    assert project_id == "project-1"


@pytest.mark.parametrize(
    "identifier_type",
    [ProjectId, DatasetId, DomainTestCaseId, RubricId, EvaluationRunId],
)
def test_identifiers_reject_empty_values(identifier_type: type[str]) -> None:
    with pytest.raises(ValueError):
        identifier_type("  ")


def test_project_dataset_test_case_and_run_reference_validate() -> None:
    project = Project(id="project-1", name="AXIOM")
    dataset = Dataset(id="dataset-1", project_id=project.id, name="Smoke cases")
    test_case = DomainTestCase(
        id="case-1",
        dataset_id=dataset.id,
        name="Health endpoint",
        inputs={"path": "/health"},
        expected_output="ok",
    )
    run_reference = EvaluationRunReference(
        id="run-1",
        project_id=project.id,
        dataset_id=dataset.id,
    )

    assert project.id == ProjectId("project-1")
    assert dataset.project_id == project.id
    assert test_case.inputs == {"path": "/health"}
    assert run_reference.model_dump() == {
        "id": "run-1",
        "project_id": "project-1",
        "dataset_id": "dataset-1",
    }


@pytest.mark.parametrize(
    "model_factory",
    [
        lambda: Project(id="project-1", name=" "),
        lambda: Dataset(id="dataset-1", project_id="project-1", name=" "),
        lambda: DomainTestCase(id="case-1", dataset_id="dataset-1", name=" ", inputs={"x": 1}),
    ],
)
def test_models_reject_blank_names(model_factory: object) -> None:
    with pytest.raises(ValidationError):
        model_factory()


def test_test_case_rejects_empty_inputs() -> None:
    with pytest.raises(ValidationError):
        DomainTestCase(id="case-1", dataset_id="dataset-1", name="Empty input", inputs={})


def test_rubric_validates_criteria() -> None:
    rubric = Rubric(
        id="rubric-1",
        project_id="project-1",
        name="Answer quality",
        criteria=["Correct", "Concise"],
    )

    assert rubric.model_dump() == {
        "id": "rubric-1",
        "project_id": "project-1",
        "name": "Answer quality",
        "criteria": ["Correct", "Concise"],
    }


@pytest.mark.parametrize("criteria", [[], ["Correct", " "]])
def test_rubric_rejects_invalid_criteria(criteria: list[str]) -> None:
    with pytest.raises(ValidationError):
        Rubric(
            id="rubric-1",
            project_id="project-1",
            name="Answer quality",
            criteria=criteria,
        )
