#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.main import app
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
        required_generated = {
            "generated_id",
            "parent_problem_id",
            "topic",
            "subtopic",
            "difficulty",
            "problem_text",
            "subparts",
            "solution",
            "solution_subparts",
            "concepts_tested",
            "variation_notes",
            "parameters",
            "functions",
            "quality_checks",
            "disabled",
            "model",
            "created_at",
        }
        assert len(generated) == 800, f"Expected 800 generated rows, found {len(generated)}"
        assert len({row["generated_id"] for row in generated}) == len(generated), "Generated IDs are not unique"
        assert len({row["problem_text"] for row in generated}) == len(generated), "Generated problem texts are not unique"

        topic_counts: dict[str, Counter[str]] = {}
        for row in generated:
            missing = required_generated - set(row)
            assert not missing, f"{row.get('generated_id')} missing generated fields: {sorted(missing)}"
            assert row.get("parent_problem_id"), row
            assert "answer:" not in row.get("problem_text", "").lower(), row.get("generated_id")
            assert row.get("solution"), row.get("generated_id")
            assert row.get("difficulty") in {"easy", "medium", "hard"}, row.get("generated_id")
            subparts = row.get("subparts", [])
            solution_subparts = row.get("solution_subparts", [])
            assert 4 <= len(subparts) <= 6, row.get("generated_id")
            assert [part.get("label") for part in subparts] == [
                part.get("label") for part in solution_subparts
            ], row.get("generated_id")
            topic_counts.setdefault(row["topic"], Counter())[row["difficulty"]] += 1

        expected_distribution = {"easy": 15, "medium": 25, "hard": 10}
        for topic, counts in topic_counts.items():
            assert dict(counts) == expected_distribution, f"{topic} difficulty counts are {dict(counts)}"

        client = TestClient(app)
        for topic in sorted(topic_counts):
            for difficulty in ("easy", "medium", "hard"):
                response = client.get("/api/problem", params={"topic": topic, "difficulty": difficulty})
                assert response.status_code == 200, response.text
                payload = response.json()
                assert payload["difficulty"] == difficulty, payload
                assert "solution" not in payload, payload
                assert "solution_subparts" not in payload, payload
                solution_response = client.get(payload["solution_url"])
                assert solution_response.status_code == 200, solution_response.text
                solution_payload = solution_response.json()
                assert [part.get("label") for part in payload["subparts"]] == [
                    part.get("label") for part in solution_payload["solution_subparts"]
                ], payload["item_id"]

    print(f"Smoke OK: {len(manifest)} sources, {len(problems)} problems, {len(solutions)} solutions.")


if __name__ == "__main__":
    main()
