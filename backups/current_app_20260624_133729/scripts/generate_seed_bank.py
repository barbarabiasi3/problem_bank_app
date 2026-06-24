#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from problem_bank_tools.seed_generation import write_seed_bank
from problem_bank_tools.utils import DEFAULT_DATA_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a deterministic verified practice bank for testing.")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    parser.add_argument("--per-topic", type=int, default=5)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    rows = write_seed_bank(Path(args.data_dir), per_topic=args.per_topic, replace=args.replace)
    print(f"Wrote {len(rows)} generated problems to {Path(args.data_dir) / 'generated_problems.jsonl'}")


if __name__ == "__main__":
    main()
