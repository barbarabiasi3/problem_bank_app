#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from problem_bank_tools.curated_bank import write_curated_bank
from problem_bank_tools.utils import DEFAULT_DATA_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a static local curated problem bank.")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    parser.add_argument("--per-topic", type=int, default=50)
    parser.add_argument("--append", action="store_true")
    args = parser.parse_args()

    rows = write_curated_bank(
        data_dir=Path(args.data_dir),
        per_topic=args.per_topic,
        replace=not args.append,
    )
    print(f"Wrote {len(rows)} curated generated problems to {Path(args.data_dir) / 'generated_problems.jsonl'}")


if __name__ == "__main__":
    main()
