from __future__ import annotations

import bisect
import difflib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .source_manifest import build_manifest
from .utils import (
    DEFAULT_BANK_DIR,
    DEFAULT_DATA_DIR,
    append_jsonl,
    compact_ws,
    data_path,
    detect_difficulty,
    detect_topic,
    ensure_data_files,
    extract_equations,
    extract_numbers,
    normalized_source_key,
    read_jsonl,
    run_text_command,
    stable_id,
    write_jsonl,
)


PROBLEM_MARKER_RE = re.compile(
    r"(?m)^\s*(?:Problem|Question)\s+([0-9]+|[IVXLC]+)\.?\s*([^\n]{0,160})"
)
NUMBERED_MARKER_RE = re.compile(r"(?m)^\s*([0-9]{1,2})[.)]?\s{2,}([A-Z][^\n]{2,160})")
SUBPART_RE = re.compile(
    r"(?m)^\s*(?:\(?([a-zA-Z])\)|([a-zA-Z])[\.)]|([ivxlcdm]+)[\.)])\s+(.+)"
)
SHORT_SECTION_RE = re.compile(
    r"(?mis)^\s*Section\s+I\s*:\s*SHORT QUESTIONS?.*?(?=^\s*Section\s+II\s*:|\Z)"
)
SOLUTION_MARKER_RE = re.compile(r"(?i)^\s*(answer|solution|answers|solutions)\s*:?\s*")


@dataclass
class TextBundle:
    text: str
    page_starts: list[int]
    pages: list[str]

    def page_for_char(self, position: int) -> int | None:
        if not self.page_starts:
            return None
        index = bisect.bisect_right(self.page_starts, position) - 1
        return index + 1 if index >= 0 else None


@dataclass
class Block:
    number: str
    title: str
    text: str
    start: int
    end: int
    page_start: int | None
    page_end: int | None


def pdf_text_bundle(path: Path) -> TextBundle:
    text = run_text_command(["pdftotext", "-layout", str(path), "-"], timeout=120)
    raw_pages = text.split("\f")
    if raw_pages and not raw_pages[-1].strip():
        raw_pages = raw_pages[:-1]
    pages = [page.rstrip() for page in raw_pages]
    joined_parts: list[str] = []
    starts: list[int] = []
    cursor = 0
    for page in pages:
        starts.append(cursor)
        joined_parts.append(page)
        cursor += len(page) + 3
    joined = "\n\f\n".join(joined_parts)
    return TextBundle(text=joined, page_starts=starts, pages=pages)


def document_text_bundle(path: Path) -> TextBundle:
    text = run_text_command(["textutil", "-convert", "txt", "-stdout", str(path)], timeout=120)
    return TextBundle(text=text, page_starts=[], pages=[text])


def read_text_bundle(source: dict[str, Any]) -> TextBundle:
    path = Path(source["path"])
    if source["file_type"] == "pdf":
        return pdf_text_bundle(path)
    return document_text_bundle(path)


def clean_title(title: str) -> str:
    title = compact_ws(title)
    title = re.sub(r"^\W+", "", title)
    return title[:140]


def find_markers(text: str) -> list[re.Match[str]]:
    markers = list(PROBLEM_MARKER_RE.finditer(text))
    if len(markers) >= 1:
        return markers
    numbered = list(NUMBERED_MARKER_RE.finditer(text))
    if len(numbered) >= 2:
        return numbered
    return []


def split_blocks(bundle: TextBundle) -> list[Block]:
    text = bundle.text
    markers = find_markers(text)
    blocks: list[Block] = []
    if markers:
        for index, marker in enumerate(markers):
            start = marker.start()
            end = markers[index + 1].start() if index + 1 < len(markers) else len(text)
            block_text = text[start:end].strip()
            if len(block_text) < 120:
                continue
            blocks.append(
                Block(
                    number=compact_ws(marker.group(1)),
                    title=clean_title(marker.group(2) or ""),
                    text=block_text,
                    start=start,
                    end=end,
                    page_start=bundle.page_for_char(start),
                    page_end=bundle.page_for_char(end),
                )
            )
    else:
        short_match = SHORT_SECTION_RE.search(text)
        if short_match:
            start, end = short_match.span()
            blocks.append(
                Block(
                    number="short",
                    title="Short Questions",
                    text=short_match.group(0).strip(),
                    start=start,
                    end=end,
                    page_start=bundle.page_for_char(start),
                    page_end=bundle.page_for_char(end),
                )
            )
    return blocks


def extract_subparts(text: str) -> list[dict[str, str]]:
    matches = list(SUBPART_RE.finditer(text))
    if len(matches) < 2:
        return []
    subparts: list[dict[str, str]] = []
    for index, match in enumerate(matches):
        label = next(group for group in match.groups()[:3] if group)
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        segment = text[start:end].strip()
        if len(segment) < 8:
            continue
        subparts.append({"label": label.lower(), "text": strip_answers_from_text(segment)[0].strip()})
    return subparts


def strip_answers_from_text(text: str) -> tuple[str, str]:
    question_lines: list[str] = []
    answer_lines: list[str] = []
    in_answer = False
    for line in text.splitlines():
        if SOLUTION_MARKER_RE.match(line):
            in_answer = True
            stripped = SOLUTION_MARKER_RE.sub("", line).strip()
            if stripped:
                answer_lines.append(stripped)
            continue
        if in_answer and SUBPART_RE.match(line):
            in_answer = False
        if in_answer:
            answer_lines.append(line)
        else:
            question_lines.append(line)
    question = "\n".join(question_lines).strip()
    answer = "\n".join(answer_lines).strip()
    return question, answer


def source_match_score(problem_key: str, solution_key: str) -> float:
    if not problem_key or not solution_key:
        return 0.0
    if problem_key == solution_key:
        return 1.0
    if problem_key in solution_key or solution_key in problem_key:
        return 0.92
    return difflib.SequenceMatcher(None, problem_key, solution_key).ratio()


def build_solution_index(sources: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    solution_sources = [
        source
        for source in sources
        if source["canonical_source"] and source["apparent_role"] in {"solutions", "both"}
    ]
    for source in solution_sources:
        try:
            bundle = read_text_bundle(source)
        except Exception as exc:
            index[source["source_id"]] = {"error": str(exc), "blocks": {}, "full_text": ""}
            continue
        blocks = split_blocks(bundle)
        block_map = {block.number.lower(): block.text for block in blocks}
        index[source["source_id"]] = {
            "source": source,
            "key": source.get("source_key") or normalized_source_key(source["path"]),
            "blocks": block_map,
            "full_text": bundle.text,
        }
    return index


def find_solution_for_block(
    source: dict[str, Any],
    block: Block,
    solution_index: dict[str, dict[str, Any]],
) -> tuple[str, str, float]:
    problem_key = source.get("source_key") or normalized_source_key(source["path"])
    best: tuple[float, dict[str, Any] | None] = (0.0, None)
    for entry in solution_index.values():
        if "source" not in entry:
            continue
        score = source_match_score(problem_key, entry["key"])
        if score > best[0]:
            best = (score, entry)
    if best[1] is None or best[0] < 0.72:
        return "", "", best[0]
    entry = best[1]
    block_solution = entry["blocks"].get(block.number.lower())
    if block_solution:
        return block_solution.strip(), entry["source"]["path"], best[0]
    if len(entry["blocks"]) == 1:
        only_solution = next(iter(entry["blocks"].values()))
        return only_solution.strip(), entry["source"]["path"], best[0]
    return "", entry["source"]["path"], best[0]


def make_problem_record(
    source: dict[str, Any],
    block: Block,
    clean_problem_text: str,
    given_solution: str,
    solution_source: str,
    match_score: float,
) -> dict[str, Any]:
    subparts = extract_subparts(clean_problem_text)
    topic, subtopic, concepts = detect_topic(clean_problem_text)
    difficulty = detect_difficulty(clean_problem_text, len(subparts))
    problem_id = stable_id("prob", source["sha256"], block.number, block.title, clean_problem_text[:800])
    notes: list[str] = []
    if not given_solution:
        notes.append("No matching provided solution found.")
    if source["extraction_confidence"] != "high":
        notes.append(f"Source extraction confidence: {source['extraction_confidence']}.")
    if match_score and match_score < 0.88:
        notes.append(f"Solution matched by fuzzy source key score {match_score:.2f}.")

    return {
        "problem_id": problem_id,
        "source_file": source["path"],
        "source_page_start": block.page_start,
        "source_page_end": block.page_end,
        "topic": topic,
        "subtopic": subtopic,
        "difficulty": difficulty,
        "problem_title": block.title,
        "problem_number": block.number,
        "problem_text": clean_problem_text,
        "subparts": subparts,
        "given_solution": given_solution,
        "verified_solution": "",
        "solution_status": "unknown",
        "concepts_tested": concepts,
        "parameters": {"numbers": extract_numbers(clean_problem_text)},
        "functions": {"detected_equations": extract_equations(clean_problem_text)},
        "notes": " ".join(notes),
        "solution_source_file": solution_source,
        "extraction_confidence": source["extraction_confidence"],
        "source_hash": source["sha256"],
    }


def make_solution_record(problem: dict[str, Any]) -> dict[str, Any]:
    return {
        "problem_id": problem["problem_id"],
        "source_file": problem["source_file"],
        "solution_source_file": problem.get("solution_source_file", ""),
        "given_solution": problem.get("given_solution", ""),
        "verified_solution": problem.get("verified_solution", ""),
        "solution_status": problem.get("solution_status", "unknown"),
        "issue_explanation": "",
        "confidence": "unverified",
        "assumptions": [],
    }


def extract_problem_bank(
    bank_dir: Path | str = DEFAULT_BANK_DIR,
    data_dir: Path | str = DEFAULT_DATA_DIR,
    rebuild_manifest: bool = True,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    ensure_data_files(data_dir)
    if rebuild_manifest or not data_path("manifest", data_dir).exists():
        manifest = build_manifest(bank_dir, data_dir)
    else:
        manifest = read_jsonl(data_path("manifest", data_dir))

    canonical_sources = [source for source in manifest if source["canonical_source"]]
    solution_index = build_solution_index(canonical_sources)
    problem_sources = [
        source
        for source in canonical_sources
        if source["apparent_role"] in {"problems", "both"}
        and source["text_readability"] != "likely_ocr_or_conversion_needed"
    ]

    problems: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []
    seen_problem_hashes: set[str] = set()
    for source in problem_sources:
        try:
            bundle = read_text_bundle(source)
            blocks = split_blocks(bundle)
        except Exception as exc:
            audit_rows.append(
                {
                    "stage": "extraction",
                    "source_file": source["path"],
                    "status": "error",
                    "message": str(exc),
                }
            )
            continue

        if not blocks:
            audit_rows.append(
                {
                    "stage": "extraction",
                    "source_file": source["path"],
                    "status": "uncertain",
                    "message": "No problem blocks detected.",
                }
            )
            continue

        for block in blocks:
            clean_problem_text, inline_solution = strip_answers_from_text(block.text)
            matched_solution, solution_source, match_score = find_solution_for_block(source, block, solution_index)
            given_solution = inline_solution or matched_solution
            fingerprint = stable_id("fp", source["source_key"], block.number, compact_ws(clean_problem_text)[:500])
            if fingerprint in seen_problem_hashes:
                continue
            seen_problem_hashes.add(fingerprint)
            problem = make_problem_record(
                source=source,
                block=block,
                clean_problem_text=clean_problem_text,
                given_solution=given_solution,
                solution_source=solution_source,
                match_score=match_score,
            )
            problems.append(problem)
            if not given_solution or problem["topic"] == "Unclassified":
                audit_rows.append(
                    {
                        "stage": "extraction",
                        "problem_id": problem["problem_id"],
                        "source_file": source["path"],
                        "status": "needs_review",
                        "message": problem["notes"] or "Unclassified topic.",
                    }
                )

    solutions = [make_solution_record(problem) for problem in problems]
    write_jsonl(data_path("problems", data_dir), problems)
    write_jsonl(data_path("solutions", data_dir), solutions)
    if not data_path("generated", data_dir).exists():
        data_path("generated", data_dir).touch()
    append_jsonl(data_path("audit", data_dir), audit_rows)
    return problems, solutions
