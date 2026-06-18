from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .gemini_client import GeminiUnavailable, configured_model, generate_json
from .utils import (
    DEFAULT_DATA_DIR,
    append_jsonl,
    data_path,
    read_jsonl,
    write_jsonl,
)


VERIFICATION_PROMPT = """You are verifying an intermediate microeconomics problem solution for teaching use.

Classify the provided solution as exactly one of:
- correct
- minor_issue
- incorrect
- incomplete
- unknown

Check algebra, calculus, optimization conditions, economics interpretation, comparative statics,
boundary cases, units/notation, assumptions, and whether the conclusion follows from the math.

Return strict JSON with these keys:
{
  "solution_status": "correct|minor_issue|incorrect|incomplete|unknown",
  "verified_solution": "A clear corrected or confirmed solution. For correct solutions, give a concise explained solution.",
  "issue_explanation": "Concise explanation of any issue, or empty string if correct.",
  "confidence": "low|medium|high",
  "assumptions": ["..."]
}

Problem:
{problem_text}

Subparts:
{subparts}

Provided solution:
{given_solution}
"""


def _problem_lookup(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["problem_id"]: row for row in rows}


def verify_solutions(
    data_dir: Path | str = DEFAULT_DATA_DIR,
    limit: int | None = None,
    model: str | None = None,
    only_unknown: bool = True,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    problems = read_jsonl(data_path("problems", data_dir))
    solutions = read_jsonl(data_path("solutions", data_dir))
    solution_by_problem = _problem_lookup(solutions)
    selected_model = model or configured_model()
    audit_rows: list[dict[str, Any]] = []
    updates = 0

    for problem in problems:
        if limit is not None and updates >= limit:
            break
        if only_unknown and problem.get("solution_status") != "unknown":
            continue
        if not problem.get("given_solution"):
            audit_rows.append(
                {
                    "stage": "verification",
                    "problem_id": problem["problem_id"],
                    "source_file": problem["source_file"],
                    "status": "unknown",
                    "message": "Skipped verification because no provided solution was extracted.",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            )
            continue

        prompt = VERIFICATION_PROMPT.format(
            problem_text=problem["problem_text"],
            subparts=problem.get("subparts", []),
            given_solution=problem.get("given_solution", ""),
        )
        try:
            result = generate_json(prompt, model=selected_model)
        except GeminiUnavailable:
            raise
        except Exception as exc:
            audit_rows.append(
                {
                    "stage": "verification",
                    "problem_id": problem["problem_id"],
                    "source_file": problem["source_file"],
                    "status": "error",
                    "message": str(exc),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            )
            continue

        status = result.get("solution_status", "unknown")
        verified_solution = result.get("verified_solution", "")
        issue = result.get("issue_explanation", "")
        confidence = result.get("confidence", "low")
        assumptions = result.get("assumptions", [])

        audit_row = {
            "stage": "verification",
            "problem_id": problem["problem_id"],
            "source_file": problem["source_file"],
            "status": status,
            "issue_explanation": issue,
            "confidence": confidence,
            "assumptions": assumptions,
            "model": selected_model,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        audit_rows.append(audit_row)
        updates += 1

        if not dry_run:
            problem["solution_status"] = status
            problem["verified_solution"] = verified_solution
            problem["notes"] = " ".join(filter(None, [problem.get("notes", ""), issue])).strip()
            solution = solution_by_problem.get(problem["problem_id"])
            if solution:
                solution["solution_status"] = status
                solution["verified_solution"] = verified_solution
                solution["issue_explanation"] = issue
                solution["confidence"] = confidence
                solution["assumptions"] = assumptions

    if audit_rows:
        append_jsonl(data_path("audit", data_dir), audit_rows)
    if updates and not dry_run:
        write_jsonl(data_path("problems", data_dir), problems)
        write_jsonl(data_path("solutions", data_dir), solutions)
    return audit_rows
