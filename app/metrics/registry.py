from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator

from app.metrics.deterministic import exact_match, json_schema_match, numeric_tolerance, regex_match
from app.metrics.models import MetricResult


class MetricSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    parameters: dict[str, JsonValue] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("name cannot be empty")
        return value


def evaluate_metric(
    spec: MetricSpec,
    *,
    actual: JsonValue,
    expected: JsonValue | None = None,
) -> MetricResult:
    if spec.name == "exact_match":
        if expected is None:
            raise ValueError("exact_match requires expected")
        return exact_match(actual, expected)

    if spec.name == "regex_match":
        pattern = _required_string(spec, "pattern")
        if not isinstance(actual, str):
            raise ValueError("regex_match requires string actual")
        return regex_match(actual, pattern)

    if spec.name == "numeric_tolerance":
        if not _is_number(actual):
            raise ValueError("numeric_tolerance requires numeric actual")
        if not _is_number(expected):
            raise ValueError("numeric_tolerance requires numeric expected")
        tolerance = spec.parameters.get("tolerance")
        if not _is_number(tolerance):
            raise ValueError("numeric_tolerance requires numeric tolerance")
        return numeric_tolerance(float(actual), float(expected), float(tolerance))

    if spec.name == "json_schema_match":
        schema = spec.parameters.get("schema")
        if not isinstance(schema, dict):
            raise ValueError("json_schema_match requires schema object")
        return json_schema_match(actual, schema)

    raise ValueError(f"unknown metric: {spec.name}")


def evaluate_metrics(
    specs: Sequence[MetricSpec],
    *,
    actual: JsonValue,
    expected: JsonValue | None = None,
) -> list[MetricResult]:
    return [evaluate_metric(spec, actual=actual, expected=expected) for spec in specs]


def _required_string(spec: MetricSpec, key: str) -> str:
    value = spec.parameters.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{spec.name} requires {key}")
    return value


def _is_number(value: object) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)
