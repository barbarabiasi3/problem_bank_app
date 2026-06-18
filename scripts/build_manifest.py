#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from problem_bank_tools.source_manifest import build_manifest
from problem_bank_tools.utils import DEFAULT_BANK_DIR, DEFAULT_DATA_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the problem-bank source manifest.")
    parser.add_argument("--bank-dir", default=str(DEFAULT_BANK_DIR))
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    args = parser.parse_args()

    rows = build_manifest(Path(args.bank_dir), Path(args.data_dir))
    print(f"Wrote {len(rows)} source records to {Path(args.data_dir) / 'source_manifest.jsonl'}")


if __name__ == "__main__":
    main()
