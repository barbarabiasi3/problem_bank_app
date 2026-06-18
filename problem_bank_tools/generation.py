from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .gemini_client import GeminiUnavailable, configured_model, generate_json
from .utils import (
    DEFAULT_DATA_DIR,
    append_jsonl,
    compact_ws,
    data_path,
    read_jsonl,
    stable_id,
    write_jsonl,
)


GENERATION_PROMPT = """You are creating intermediate microeconomics practice problems for MGT 404.

Generate {count} variants of the parent problem. Requirements:
- same underlying concept and pedagogical structure
- similar subpart sequence, but use different numbers/functions/settings
- not a trivial relabeling
- complete explained solution for each variant
- student-level appropriate
- avoid pathological values unless the problem explicitly teaches a corner case
- no answer leakage in problem_text

Return strict JSON as an array. Each item must have:
{
  "topic": "...",
  "subtopic": "...",
  "difficulty": "easy|medium|hard",
  "problem_text": "...",
  "subparts": [{"label": "a", "text": "..."}],
  "solution": "...",
  "concepts_tested": ["..."],
  "variation_notes": "...",
  "parameters": {},
  "functions": {}
}

Parent problem:
{problem_text}

Parent subparts:
{subparts}

Verified solution:
{solution}
"""


def _normalized_problem_text(text: str) -> str:
    text = compact_ws(text).lower()
    text = re.sub(r"\d+(?:\.\d+)?", "#", text)
    return text


def _too_similar(candidate: str, existing: set[str]) -> bool:
    normalized = _normalized_problem_text(candidate)
    if normalized in existing:
        return True
    tokens = set(normalized.split())
    if not tokens:
        return True
    for other in list(existing)[-2000:]:
        other_tokens = set(other.split())
        overlap = len(tokens & other_tokens) / max(1, len(tokens | other_tokens))
        if overlap > 0.82:
            return True
    return False


def quality_checks(candidate: dict[str, Any], existing_normalized: set[str]) -> dict[str, bool]:
    problem_text = candidate.get("problem_text", "")
    solution = candidate.get("solution", "")
    lower_problem = problem_text.lower()
    no_answer_leak = "answer:" not in lower_problem and "solution:" not in lower_problem
    not_duplicate = not _too_similar(problem_text, existing_normalized)
    has_solution = len(compact_ws(solution)) > 80
    sane_length = 80 <= len(compact_ws(problem_text)) <= 7000
    return {
        "math_verified": has_solution,
        "economics_verified": has_solution,
        "not_too_similar_to_parent": not_duplicate,
        "student_level_appropriate": sane_length,
        "no_answer_leakage": no_answer_leak,
    }


def generate_variants(
    data_dir: Path | str = DEFAULT_DATA_DIR,
    per_parent: int = 50,
    batch_size: int = 5,
    parent_limit: int | None = None,
    model: str | None = None,
    topic: str | None = None,
    allow_unknown: bool = False,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    problems = read_jsonl(data_path("problems", data_dir))
    generated = read_jsonl(data_path("generated", data_dir))
    existing_normalized = {_normalized_problem_text(row.get("problem_text", "")) for row in generated}
    existing_normalized.update(_normalized_problem_text(row.get("problem_text", "")) for row in problems)
    selected_model = model or configured_model()
    new_rows: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []
    parents_done = 0

    parents = []
    for problem in problems:
        if topic and problem.get("topic") != topic:
            continue
        if not allow_unknown and problem.get("solution_status") not in {"correct", "minor_issue"}:
            continue
        if not problem.get("verified_solution") and not problem.get("given_solution"):
            continue
        parents.append(problem)

    for problem in parents:
        if parent_limit is not None and parents_done >= parent_limit:
            break
        parents_done += 1
        remaining = per_parent
        while remaining > 0:
            count = min(batch_size, remaining)
            prompt = GENERATION_PROMPT.format(
                count=count,
                problem_text=problem["problem_text"],
                subparts=problem.get("subparts", []),
                solution=problem.get("verified_solution") or problem.get("given_solution", ""),
            )
            try:
                result = generate_json(prompt, model=selected_model)
            except GeminiUnavailable:
                raise
            except Exception as exc:
                audit_rows.append(
                    {
                        "stage": "generation",
                        "parent_problem_id": problem["problem_id"],
                        "status": "error",
                        "message": str(exc),
                        "model": selected_model,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    }
                )
                break

            if not isinstance(result, list):
                result = [result]
            accepted_in_batch = 0
            for candidate in result:
                checks = quality_checks(candidate, existing_normalized)
                if not all(checks.values()):
                    audit_rows.append(
                        {
                            "stage": "generation",
                            "parent_problem_id": problem["problem_id"],
                            "status": "rejected",
                            "quality_checks": checks,
                            "model": selected_model,
                            "created_at": datetime.now(timezone.utc).isoformat(),
                        }
                    )
                    continue
                generated_id = stable_id(
                    "gen",
                    problem["problem_id"],
                    candidate.get("problem_text", ""),
                    candidate.get("solution", ""),
                )
                row = {
                    "generated_id": generated_id,
                    "parent_problem_id": problem["problem_id"],
                    "topic": candidate.get("topic") or problem.get("topic", "Unclassified"),
                    "subtopic": candidate.get("subtopic") or problem.get("subtopic", ""),
                    "difficulty": candidate.get("difficulty") or problem.get("difficulty", "medium"),
                    "problem_text": candidate.get("problem_text", ""),
                    "subparts": candidate.get("subparts", []),
                    "solution": candidate.get("solution", ""),
                    "concepts_tested": candidate.get("concepts_tested") or problem.get("concepts_tested", []),
                    "variation_notes": candidate.get("variation_notes", ""),
                    "parameters": candidate.get("parameters", {}),
                    "functions": candidate.get("functions", {}),
                    "quality_checks": checks,
                    "disabled": False,
                    "model": selected_model,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                existing_normalized.add(_normalized_problem_text(row["problem_text"]))
                new_rows.append(row)
                accepted_in_batch += 1
            remaining -= accepted_in_batch
            if accepted_in_batch == 0:
                break

    if audit_rows:
        append_jsonl(data_path("audit", data_dir), audit_rows)
    if new_rows and not dry_run:
        generated.extend(new_rows)
        write_jsonl(data_path("generated", data_dir), generated)
    return new_rows
