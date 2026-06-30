from __future__ import annotations

import re
from math import isfinite
from typing import Any

from pydantic import JsonValue

from app.metrics.models import MetricResult


def _result(name: str, passed: bool, details: dict[str, JsonValue] | None = None) -> MetricResult:
    return MetricResult(
        name=name,
        passed=passed,
        score=1.0 if passed else 0.0,
        details=details or {},
    )


def exact_match(actual: JsonValue, expected: JsonValue) -> MetricResult:
    return _result(
        "exact_match",
        actual == expected,
        {"actual": actual, "expected": expected},
    )


def regex_match(actual: str, pattern: str) -> MetricResult:
    try:
        compiled = re.compile(pattern)
    except re.error as exc:
        raise ValueError(f"invalid regex pattern: {exc}") from exc

    passed = compiled.search(actual) is not None
    return _result("regex_match", passed, {"actual": actual, "pattern": pattern})


def numeric_tolerance(actual: float, expected: float, tolerance: float) -> MetricResult:
    if tolerance < 0:
        raise ValueError("tolerance cannot be negative")
    if not (isfinite(actual) and isfinite(expected) and isfinite(tolerance)):
        raise ValueError("actual, expected, and tolerance must be finite")

    difference = abs(actual - expected)
    return _result(
        "numeric_tolerance",
        difference <= tolerance,
        {
            "actual": actual,
            "expected": expected,
            "tolerance": tolerance,
            "difference": difference,
        },
    )


def json_schema_match(value: JsonValue, schema: dict[str, JsonValue]) -> MetricResult:
    errors: list[str] = []
    _validate_schema_value(value, schema, "$", errors)
    return _result("json_schema_match", not errors, {"errors": errors})


def _validate_schema_value(
    value: JsonValue,
    schema: dict[str, Any],
    path: str,
    errors: list[str],
) -> None:
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}")

    if "enum" in schema:
        enum_values = schema["enum"]
        if not isinstance(enum_values, list):
            errors.append(f"{path}: enum must be a list")
        elif value not in enum_values:
            errors.append(f"{path}: value is not in enum")

    expected_type = schema.get("type")
    if expected_type is not None:
        if not isinstance(expected_type, str):
            errors.append(f"{path}: type must be a string")
        elif not _matches_type(value, expected_type):
            errors.append(f"{path}: expected type {expected_type}")
            return

    if expected_type == "object":
        if not isinstance(value, dict):
            return
        required = schema.get("required", [])
        if not isinstance(required, list):
            errors.append(f"{path}: required must be a list")
        else:
            for key in required:
                if not isinstance(key, str):
                    errors.append(f"{path}: required entries must be strings")
                elif key not in value:
                    errors.append(f"{path}: missing required property {key}")

        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            errors.append(f"{path}: properties must be an object")
        else:
            for key, child_schema in properties.items():
                if key in value:
                    if not isinstance(child_schema, dict):
                        errors.append(f"{path}.{key}: property schema must be an object")
                    else:
                        _validate_schema_value(value[key], child_schema, f"{path}.{key}", errors)

    if expected_type == "array":
        if not isinstance(value, list):
            return
        items = schema.get("items")
        if items is None:
            return
        if not isinstance(items, dict):
            errors.append(f"{path}: items must be an object")
            return
        for index, item in enumerate(value):
            _validate_schema_value(item, items, f"{path}[{index}]", errors)


def _matches_type(value: JsonValue, expected_type: str) -> bool:
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "number":
        return isinstance(value, int | float) and not isinstance(value, bool)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "null":
        return value is None
    raise ValueError(f"unsupported schema type: {expected_type}")
