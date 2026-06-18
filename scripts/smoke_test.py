#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from problem_bank_tools.utils import DEFAULT_DATA_DIR, data_path, read_jsonl


def main() -> None:
    problems_path = data_path("problems", DEFAULT_DATA_DIR)
    solutions_path = data_path("solutions", DEFAULT_DATA_DIR)
    manifest_path = data_path("manifest", DEFAULT_DATA_DIR)
    assert manifest_path.exists(), "Missing source manifest."
    assert problems_path.exists(), "Missing problems.jsonl."
    assert solutions_path.exists(), "Missing solutions.jsonl."

    manifest = read_jsonl(manifest_path)
    problems = read_jsonl(problems_path)
    solutions = read_jsonl(solutions_path)
    assert manifest, "Manifest is empty."
    assert problems, "No problems extracted."
    assert len(problems) == len(solutions), "Problems and solutions counts do not match."

    required = {
        "problem_id",
        "source_file",
        "topic",
        "difficulty",
        "problem_text",
        "subparts",
        "given_solution",
        "verified_solution",
        "solution_status",
        "concepts_tested",
        "parameters",
        "functions",
        "notes",
    }
    for problem in problems:
        missing = required - set(problem)
        assert not missing, f"{problem.get('problem_id')} missing fields: {sorted(missing)}"
        assert problem["solution_status"] in {"correct", "minor_issue", "incorrect", "incomplete", "unknown"}
        assert "solution:" not in problem["problem_text"].lower(), problem["problem_id"]

    generated_path = data_path("generated", DEFAULT_DATA_DIR)
    if generated_path.exists() and Path(generated_path).stat().st_size:
        generated = read_jsonl(generated_path)
        for row in generated:
            assert row.get("parent_problem_id"), row
            assert "answer:" not in row.get("problem_text", "").lower(), row.get("generated_id")
            assert row.get("solution"), row.get("generated_id")

    print(f"Smoke OK: {len(manifest)} sources, {len(problems)} problems, {len(solutions)} solutions.")


if __name__ == "__main__":
    main()
