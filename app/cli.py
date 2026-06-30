from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from typing import TextIO

from app.ci_gate import GateInputError, gate_exit_code, load_gate_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="axiom")
    subparsers = parser.add_subparsers(dest="command", required=True)

    gate_parser = subparsers.add_parser("gate")
    gate_parser.add_argument("--result-file", required=True)

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

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
