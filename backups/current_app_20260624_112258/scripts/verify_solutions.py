#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from problem_bank_tools.gemini_client import GeminiUnavailable
from problem_bank_tools.utils import DEFAULT_DATA_DIR
from problem_bank_tools.verification import verify_solutions


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify extracted solutions with Gemini.")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    parser.add_argument("--model", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--include-reviewed", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        rows = verify_solutions(
            data_dir=Path(args.data_dir),
            limit=args.limit,
            model=args.model,
            only_unknown=not args.include_reviewed,
            dry_run=args.dry_run,
        )
    except GeminiUnavailable as exc:
        raise SystemExit(f"Gemini is not configured: {exc}") from exc
    print(f"Verification audit rows: {len(rows)}")


if __name__ == "__main__":
    main()
