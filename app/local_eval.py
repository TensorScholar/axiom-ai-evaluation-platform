from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, JsonValue, ValidationError, field_validator

from app.domain import TestCase
from app.evaluations import EvaluationRunMetadata, EvaluationRunRecord, run_evaluation_cases
from app.providers import FakeProvider, ProviderResponse


class LocalEvalInputError(ValueError):
    pass


class LocalEvalDatasetFixture(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_id: str
    project_id: str
    dataset_id: str
    model_name: str
    metadata: EvaluationRunMetadata
    test_cases: list[TestCase]
    provider_parameters: dict[str, JsonValue] = Field(default_factory=dict)

    @field_validator("run_id", "project_id", "dataset_id", "model_name")
    @classmethod
    def required_text_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("value cannot be empty")
        return value

    @field_validator("test_cases")
    @classmethod
    def test_cases_must_not_be_empty(cls, value: list[TestCase]) -> list[TestCase]:
        if not value:
            raise ValueError("test_cases cannot be empty")
        return value


class LocalEvalProviderFixture(BaseModel):
    model_config = ConfigDict(frozen=True)

    responses: list[ProviderResponse | str] = Field(default_factory=list)
    echo_fallback: bool = True


def run_local_eval_from_files(
    *,
    dataset_file: str | Path,
    provider_file: str | Path,
    output_file: str | Path,
) -> EvaluationRunRecord:
    dataset = _load_dataset_fixture(dataset_file)
    provider_fixture = _load_provider_fixture(provider_file)
    provider = FakeProvider(
        provider_fixture.responses,
        echo_fallback=provider_fixture.echo_fallback,
    )
    run = run_evaluation_cases(
        run_id=dataset.run_id,
        project_id=dataset.project_id,
        dataset_id=dataset.dataset_id,
        test_cases=dataset.test_cases,
        provider=provider,
        model_name=dataset.model_name,
        metadata=dataset.metadata,
        provider_parameters=dataset.provider_parameters,
    )
    _write_result(output_file, run)
    return run


def _load_dataset_fixture(path: str | Path) -> LocalEvalDatasetFixture:
    payload = _load_json_object(path, "dataset")
    try:
        return LocalEvalDatasetFixture.model_validate(payload)
    except ValidationError as exc:
        raise LocalEvalInputError(f"invalid dataset fixture: {exc}") from exc


def _load_provider_fixture(path: str | Path) -> LocalEvalProviderFixture:
    payload = _load_json_object(path, "provider")
    try:
        return LocalEvalProviderFixture.model_validate(payload)
    except ValidationError as exc:
        raise LocalEvalInputError(f"invalid provider fixture: {exc}") from exc


def _load_json_object(path: str | Path, label: str) -> dict[str, Any]:
    source = Path(path)
    try:
        raw = source.read_text(encoding="utf-8")
    except OSError as exc:
        raise LocalEvalInputError(f"could not read {label} file: {source}") from exc

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise LocalEvalInputError(f"invalid JSON in {label} file: {source}") from exc

    if not isinstance(payload, dict):
        raise LocalEvalInputError(f"{label} fixture must be an object")
    return payload


def _write_result(path: str | Path, run: EvaluationRunRecord) -> None:
    output = Path(path)
    try:
        output.write_text(
            json.dumps(run.model_dump(mode="json"), indent=2, sort_keys=True),
            encoding="utf-8",
        )
    except OSError as exc:
        raise LocalEvalInputError(f"could not write result file: {output}") from exc
