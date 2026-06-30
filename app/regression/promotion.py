from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.domain import TestCase
from app.evaluations import EvaluationRunMetadata, EvaluationRunRecord, SampleOutcome, SampleResult
from app.regression.models import RegressionSuite
from app.regression.suite import build_regression_suite, failure_to_regression_case


class RegressionPromotionError(ValueError):
    pass


class RegressionPromotionResult(BaseModel):
    model_config = ConfigDict(frozen=True, use_enum_values=True)

    source_run_id: str
    project_id: str
    dataset_id: str
    source_metadata: EvaluationRunMetadata
    suite: RegressionSuite
    promoted_count: int = Field(ge=0)
    skipped_duplicate_count: int = Field(ge=0)


def promote_failed_samples_to_regression_suite(
    *,
    run: EvaluationRunRecord,
    test_cases: Sequence[TestCase],
    suite_id: str,
    suite_name: str,
) -> RegressionPromotionResult:
    test_case_by_id = _index_test_cases(test_cases)
    promoted_case_ids: set[str] = set()
    skipped_duplicate_count = 0
    regression_cases = []

    for sample in run.sample_results:
        failure_reason = _sample_failure_reason(sample)
        if failure_reason is None:
            continue
        test_case_id = str(sample.test_case_id)
        if test_case_id in promoted_case_ids:
            skipped_duplicate_count += 1
            continue
        test_case = test_case_by_id.get(test_case_id)
        if test_case is None:
            raise RegressionPromotionError(f"missing test case for failed sample: {test_case_id}")

        promoted_case_ids.add(test_case_id)
        regression_cases.append(
            failure_to_regression_case(
                regression_case_id=f"regression-{run.id}-{test_case.id}",
                source_run_id=run.id,
                test_case_id=test_case.id,
                dataset_id=test_case.dataset_id,
                name=test_case.name,
                inputs=test_case.inputs,
                failure_reason=failure_reason,
                expected_output=test_case.expected_output,
            )
        )

    if not regression_cases:
        raise RegressionPromotionError("no failed samples to promote")

    suite = build_regression_suite(suite_id=suite_id, name=suite_name, cases=regression_cases)
    return RegressionPromotionResult(
        source_run_id=run.id,
        project_id=run.project_id,
        dataset_id=run.dataset_id,
        source_metadata=run.metadata,
        suite=suite,
        promoted_count=len(regression_cases),
        skipped_duplicate_count=skipped_duplicate_count,
    )


def run_regression_promotion_from_files(
    *,
    run_file: str | Path,
    test_cases_file: str | Path,
    output_file: str | Path,
    suite_id: str,
    suite_name: str,
) -> RegressionPromotionResult:
    run = _load_run(run_file)
    test_cases = _load_test_cases(test_cases_file)
    result = promote_failed_samples_to_regression_suite(
        run=run,
        test_cases=test_cases,
        suite_id=suite_id,
        suite_name=suite_name,
    )
    _write_result(output_file, result)
    return result


def _index_test_cases(test_cases: Sequence[TestCase]) -> dict[str, TestCase]:
    if not test_cases:
        raise RegressionPromotionError("test_cases cannot be empty")

    indexed: dict[str, TestCase] = {}
    for test_case in test_cases:
        test_case_id = str(test_case.id)
        if test_case_id in indexed:
            raise RegressionPromotionError(f"duplicate test case id: {test_case_id}")
        indexed[test_case_id] = test_case
    return indexed


def _sample_failure_reason(sample: SampleResult) -> str | None:
    if sample.outcome == SampleOutcome.ERRORED:
        return sample.error_message

    failed_metrics = []
    metrics = sample.metadata.get("metrics", [])
    if isinstance(metrics, list):
        for metric in metrics:
            if not isinstance(metric, dict) or metric.get("passed") is not False:
                continue
            name = metric.get("name")
            if isinstance(name, str) and name.strip():
                failed_metrics.append(f"metric {name} failed")
            else:
                failed_metrics.append("metric failed")

    if failed_metrics:
        return "; ".join(failed_metrics)
    return None


def _load_run(path: str | Path) -> EvaluationRunRecord:
    payload = _load_json_object(path, "run")
    try:
        return EvaluationRunRecord.model_validate(payload)
    except ValidationError as exc:
        raise RegressionPromotionError(f"invalid run file: {exc}") from exc


def _load_test_cases(path: str | Path) -> list[TestCase]:
    payload = _load_json(path, "test cases")
    raw_cases: Any
    if isinstance(payload, dict):
        raw_cases = payload.get("test_cases")
    else:
        raw_cases = payload
    if not isinstance(raw_cases, list):
        raise RegressionPromotionError("test cases file must contain a list or test_cases list")
    try:
        return [TestCase.model_validate(item) for item in raw_cases]
    except ValidationError as exc:
        raise RegressionPromotionError(f"invalid test cases file: {exc}") from exc


def _load_json_object(path: str | Path, label: str) -> dict[str, Any]:
    payload = _load_json(path, label)
    if not isinstance(payload, dict):
        raise RegressionPromotionError(f"{label} file must contain a JSON object")
    return payload


def _load_json(path: str | Path, label: str) -> Any:
    source = Path(path)
    try:
        raw = source.read_text(encoding="utf-8")
    except OSError as exc:
        raise RegressionPromotionError(f"could not read {label} file: {source}") from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RegressionPromotionError(f"invalid JSON in {label} file: {source}") from exc


def _write_result(path: str | Path, result: RegressionPromotionResult) -> None:
    output = Path(path)
    try:
        output.write_text(
            json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True),
            encoding="utf-8",
        )
    except OSError as exc:
        raise RegressionPromotionError(f"could not write regression promotion result: {output}") from exc
