from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT / "data"
DEFAULT_BANK_DIR = ROOT / "problem_bank"

DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".doc"}
DATA_FILES = {
    "manifest": "source_manifest.jsonl",
    "problems": "problems.jsonl",
    "solutions": "solutions.jsonl",
    "generated": "generated_problems.jsonl",
    "audit": "audit_log.jsonl",
}

TOPIC_KEYWORDS: list[tuple[str, list[str]]] = [
    ("Supply and Demand", ["supply", "demand", "equilibrium price", "quantity demanded", "quantity supplied"]),
    ("Elasticity", ["elasticity", "inelastic", "elastic", "price sensitivity", "percentage change"]),
    ("Taxes and Government Intervention", ["tax", "tariff", "quota", "price floor", "price ceiling", "deadweight", "government revenue"]),
    ("Trade and Welfare", ["trade", "import", "export", "world price", "producer surplus", "consumer surplus", "domestic surplus"]),
    ("Production and Costs", ["cost function", "marginal cost", "average cost", "fixed cost", "variable cost", "production function"]),
    ("Perfect Competition", ["perfectly competitive", "competitive market", "free entry", "shutdown", "long-run equilibrium"]),
    ("Monopoly", ["monopoly", "monopolist", "inverse demand", "marginal revenue", "markup", "iepr"]),
    ("Price Discrimination", ["price discriminate", "price discrimination", "two-part tariff", "membership", "self-selecting", "segments"]),
    ("Risk and Insurance", ["risk", "insurance", "certainty equivalent", "risk premium", "expected utility", "warranty"]),
    ("Asymmetric Information", ["adverse selection", "moral hazard", "hidden action", "hidden type", "asymmetric information"]),
    ("Incentives and Contracts", ["bonus", "incentive", "effort", "wage", "constraint", "participation constraint"]),
    ("Game Theory", ["nash", "dominant strategy", "game tree", "simultaneously", "payoff", "price competition"]),
    ("Oligopoly and Strategic Competition", ["bertrand", "cournot", "capacity", "price leader", "oligopoly"]),
    ("Externalities and Public Goods", ["externality", "public good", "social cost", "social benefit", "mandate"]),
    ("Consumer Choice", ["utility", "budget constraint", "consumer choice", "willingness to pay", "reservation price"]),
]


def data_path(name: str, data_dir: Path | str = DEFAULT_DATA_DIR) -> Path:
    return Path(data_dir) / DATA_FILES[name]


def ensure_data_files(data_dir: Path | str = DEFAULT_DATA_DIR) -> None:
    data = Path(data_dir)
    data.mkdir(parents=True, exist_ok=True)
    for file_name in DATA_FILES.values():
        path = data / file_name
        if not path.exists():
            path.touch()


def read_jsonl(path: Path | str) -> list[dict[str, Any]]:
    file_path = Path(path)
    if not file_path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with file_path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL in {file_path}:{line_no}: {exc}") from exc
    return rows


def write_jsonl(path: Path | str, rows: Iterable[dict[str, Any]]) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def append_jsonl(path: Path | str, rows: Iterable[dict[str, Any]]) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def run_text_command(args: list[str], timeout: int = 60) -> str:
    result = subprocess.run(args, text=True, capture_output=True, timeout=timeout, check=False)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(args)}\n{result.stderr.strip()}"
        )
    return result.stdout


def sha256_file(path: Path | str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_id(prefix: str, *parts: Any) -> str:
    raw = "\n".join(str(part) for part in parts)
    return f"{prefix}_{hashlib.sha1(raw.encode('utf-8')).hexdigest()[:16]}"


def slugify(value: str, default: str = "untitled") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or default


def compact_ws(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def text_char_count(value: str) -> int:
    return len(re.sub(r"\s+", "", value))


def classify_role(path: Path | str) -> str:
    name = Path(path).name.lower()
    if "student" in name and "solution" in name:
        return "student_solutions"
    if re.search(r"with[_\s-]*solutions?|draft with solutions?", name):
        return "both"
    if re.search(r"solutions?|_sol\b| sol\.pdf$|- sol\.", name):
        return "solutions"
    return "problems"


def normalized_source_key(path: Path | str) -> str:
    stem = Path(path).stem.lower()
    replacements = [
        "with solutions for posting",
        "with solutions for students",
        "with solutions",
        "student solutions",
        "solutions",
        "solution",
        "draft",
        "for posting",
        "for students",
        "no sols",
        "sol",
    ]
    for item in replacements:
        stem = stem.replace(item, " ")
    stem = re.sub(r"\b(old|copy)\b", " ", stem)
    stem = re.sub(r"[^a-z0-9]+", " ", stem)
    return compact_ws(stem)


def detect_topic(text: str) -> tuple[str, str, list[str]]:
    lower = text.lower()
    scores: list[tuple[int, str, list[str]]] = []
    for topic, keywords in TOPIC_KEYWORDS:
        score = sum(lower.count(keyword) for keyword in keywords)
        if score:
            scores.append((score, topic, keywords))
    if not scores:
        return "Unclassified", "", []
    scores.sort(reverse=True, key=lambda item: item[0])
    topic = scores[0][1]
    concepts = [keyword for keyword in scores[0][2] if keyword in lower][:5]
    subtopic = concepts[0].title() if concepts else ""
    return topic, subtopic, concepts


def detect_difficulty(text: str, subpart_count: int) -> str:
    lower = text.lower()
    score = 0
    score += 1 if len(text) > 1400 else 0
    score += 1 if subpart_count >= 4 else 0
    score += 1 if any(word in lower for word in ["challenge", "nash", "derive", "prove", "compare"]) else 0
    score += 1 if any(word in lower for word in ["calculus", "maximize", "minimize", "marginal"]) else 0
    if score >= 3:
        return "hard"
    if score >= 1:
        return "medium"
    return "easy"


def extract_equations(text: str, limit: int = 12) -> list[str]:
    equations: list[str] = []
    for raw_line in text.splitlines():
        line = compact_ws(raw_line)
        if len(line) < 5 or len(line) > 180:
            continue
        if "=" in line or re.search(r"\b(Q|P|MC|MR|AC|TC|CS|PS)\b", line):
            equations.append(line)
        if len(equations) >= limit:
            break
    return equations


def extract_numbers(text: str, limit: int = 40) -> list[str]:
    values = re.findall(r"(?<![A-Za-z])\$?-?\d+(?:,\d{3})*(?:\.\d+)?%?", text)
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            unique.append(value)
        if len(unique) >= limit:
            break
    return unique


def load_dotenv(path: Path | str = ROOT / ".env") -> None:
    file_path = Path(path)
    if not file_path.exists():
        return
    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)
