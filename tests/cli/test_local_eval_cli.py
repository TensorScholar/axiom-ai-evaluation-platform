import json
from io import StringIO

from app.cli import main


def write_json(path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def dataset_fixture() -> dict[str, object]:
    return {
        "run_id": "run-020",
        "project_id": "project-1",
        "dataset_id": "dataset-1",
        "model_name": "fake-model",
        "metadata": {
            "spec_version": "spec-020",
            "code_version": "cli-test",
            "dataset_fingerprint": "dataset-fp",
            "seed": 0,
            "parameters": {},
        },
        "provider_parameters": {"temperature": 0},
        "test_cases": [
            {
                "id": "case-1",
                "dataset_id": "dataset-1",
                "name": "Says ok",
                "inputs": {"prompt": "Say ok"},
                "expected_output": "ok",
            }
        ],
    }


def test_eval_cli_runs_fake_provider_and_writes_result(tmp_path) -> None:
    dataset_file = tmp_path / "dataset.json"
    provider_file = tmp_path / "provider.json"
    output_file = tmp_path / "result.json"
    write_json(dataset_file, dataset_fixture())
    write_json(
        provider_file,
        {
            "responses": [
                {"text": "ok", "model_name": "fake-model", "metadata": {"tokens": 1}}
            ]
        },
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "eval",
            "--dataset-file",
            str(dataset_file),
            "--provider-file",
            str(provider_file),
            "--output-file",
            str(output_file),
        ],
        stdout=stdout,
        stderr=stderr,
    )

    result = json.loads(output_file.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert stdout.getvalue() == "AXIOM eval completed: run-020\n"
    assert stderr.getvalue() == ""
    assert result["status"] == "completed"
    assert result["sample_results"][0]["output"] == "ok"
    assert result["sample_results"][0]["metadata"]["metrics"][0]["passed"] is True


def test_eval_cli_returns_two_for_invalid_dataset(tmp_path) -> None:
    dataset_file = tmp_path / "dataset.json"
    provider_file = tmp_path / "provider.json"
    output_file = tmp_path / "result.json"
    write_json(dataset_file, {"run_id": " "})
    write_json(provider_file, {"responses": []})
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "eval",
            "--dataset-file",
            str(dataset_file),
            "--provider-file",
            str(provider_file),
            "--output-file",
            str(output_file),
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert stderr.getvalue().startswith("AXIOM eval error: invalid dataset fixture:")
