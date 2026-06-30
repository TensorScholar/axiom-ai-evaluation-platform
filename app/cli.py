from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from typing import TextIO

from app.ci_gate import (
    GateInputError,
    gate_exit_code,
    gate_result_from_summary,
    load_evaluation_summary,
    load_gate_result,
    write_gate_result,
)
from app.local_eval import LocalEvalInputError, run_local_eval_from_files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="axiom")
    subparsers = parser.add_subparsers(dest="command", required=True)

    gate_parser = subparsers.add_parser("gate")
    gate_parser.add_argument("--result-file", required=True)

    eval_parser = subparsers.add_parser("eval")
    eval_parser.add_argument("--dataset-file", required=True)
    eval_parser.add_argument("--provider-file", required=True)
    eval_parser.add_argument("--output-file", required=True)

    summary_gate_parser = subparsers.add_parser("summarize-gate")
    summary_gate_parser.add_argument("--summary-file", required=True)
    summary_gate_parser.add_argument("--output-file", required=True)
    summary_gate_parser.add_argument("--min-pass-rate", type=float, default=1.0)
    summary_gate_parser.add_argument("--max-error-rate", type=float, default=0.0)

    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "gate":
        try:
            result = load_gate_result(args.result_file)
        except GateInputError as exc:
            print(f"AXIOM gate error: {exc}", file=stderr)
            return 2

        exit_code = gate_exit_code(result)
        if exit_code == 0:
            print(f"AXIOM gate passed: {result.suite_id}", file=stdout)
        else:
            print(f"AXIOM gate failed: {result.suite_id}", file=stdout)
        return exit_code

    if args.command == "eval":
        try:
            run = run_local_eval_from_files(
                dataset_file=args.dataset_file,
                provider_file=args.provider_file,
                output_file=args.output_file,
            )
        except LocalEvalInputError as exc:
            print(f"AXIOM eval error: {exc}", file=stderr)
            return 2

        print(f"AXIOM eval completed: {run.id}", file=stdout)
        return 0

    if args.command == "summarize-gate":
        try:
            summary = load_evaluation_summary(args.summary_file)
            result = gate_result_from_summary(
                summary,
                min_pass_rate=args.min_pass_rate,
                max_error_rate=args.max_error_rate,
            )
            write_gate_result(args.output_file, result)
        except GateInputError as exc:
            print(f"AXIOM summarize-gate error: {exc}", file=stderr)
            return 2

        print(f"AXIOM gate result written: {result.suite_id}", file=stdout)
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
