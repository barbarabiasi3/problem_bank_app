#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from problem_bank_tools.extraction import extract_problem_bank
from problem_bank_tools.utils import DEFAULT_BANK_DIR, DEFAULT_DATA_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract structured problems and solutions.")
    parser.add_argument("--bank-dir", default=str(DEFAULT_BANK_DIR))
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    parser.add_argument("--no-rebuild-manifest", action="store_true")
    args = parser.parse_args()

    problems, solutions = extract_problem_bank(
        bank_dir=Path(args.bank_dir),
        data_dir=Path(args.data_dir),
        rebuild_manifest=not args.no_rebuild_manifest,
    )
    with_solutions = sum(1 for problem in problems if problem.get("given_solution"))
    print(f"Extracted {len(problems)} problems.")
    print(f"Wrote {len(solutions)} solution records.")
    print(f"{with_solutions} problems have a matched or inline provided solution.")


if __name__ == "__main__":
    main()
