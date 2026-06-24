#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from problem_bank_tools.gemini_client import GeminiUnavailable
from problem_bank_tools.generation import generate_variants
from problem_bank_tools.utils import DEFAULT_DATA_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate verified problem variants in batches.")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    parser.add_argument("--model", default=None)
    parser.add_argument("--topic", default=None)
    parser.add_argument("--per-parent", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=5)
    parser.add_argument("--parent-limit", type=int, default=None)
    parser.add_argument("--allow-unknown", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        rows = generate_variants(
            data_dir=Path(args.data_dir),
            per_parent=args.per_parent,
            batch_size=args.batch_size,
            parent_limit=args.parent_limit,
            model=args.model,
            topic=args.topic,
            allow_unknown=args.allow_unknown,
            dry_run=args.dry_run,
        )
    except GeminiUnavailable as exc:
        raise SystemExit(f"Gemini is not configured: {exc}") from exc
    print(f"Accepted generated variants: {len(rows)}")


if __name__ == "__main__":
    main()
