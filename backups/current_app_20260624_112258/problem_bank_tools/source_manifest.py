from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from .utils import (
    DEFAULT_BANK_DIR,
    DEFAULT_DATA_DIR,
    DOCUMENT_EXTENSIONS,
    classify_role,
    compact_ws,
    data_path,
    ensure_data_files,
    normalized_source_key,
    run_text_command,
    sha256_file,
    text_char_count,
    write_jsonl,
)


@dataclass
class SourceRecord:
    source_id: str
    path: str
    file_name: str
    file_type: str
    sha256: str
    duplicate_group: str
    canonical_source: bool
    apparent_role: str
    page_count: int | None
    text_readability: str
    text_char_count_sample: int
    extraction_confidence: str
    source_key: str
    notes: str


def iter_source_files(bank_dir: Path | str = DEFAULT_BANK_DIR) -> Iterable[Path]:
    root = Path(bank_dir)
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.name == ".DS_Store" or path.name.lower() == "icon":
            continue
        if path.suffix.lower() in DOCUMENT_EXTENSIONS:
            yield path


def pdf_page_count(path: Path) -> int | None:
    try:
        output = run_text_command(["pdfinfo", str(path)], timeout=30)
    except Exception:
        return None
    for line in output.splitlines():
        if line.startswith("Pages:"):
            try:
                return int(line.split(":", 1)[1].strip())
            except ValueError:
                return None
    return None


def pdf_sample_text(path: Path, page_limit: int = 2) -> str:
    args = ["pdftotext", "-q", "-f", "1", "-l", str(page_limit), str(path), "-"]
    try:
        return run_text_command(args, timeout=60)
    except Exception:
        return ""


def document_sample_text(path: Path) -> str:
    try:
        return run_text_command(["textutil", "-convert", "txt", "-stdout", str(path)], timeout=60)
    except Exception:
        return ""


def document_page_count(path: Path) -> int | None:
    try:
        output = run_text_command(["file", str(path)], timeout=30)
    except Exception:
        return None
    match = re.search(r"Number of Pages:\s*(\d+)", output)
    return int(match.group(1)) if match else None


def build_manifest(
    bank_dir: Path | str = DEFAULT_BANK_DIR,
    data_dir: Path | str = DEFAULT_DATA_DIR,
) -> list[dict]:
    ensure_data_files(data_dir)
    paths = list(iter_source_files(bank_dir))
    hash_by_path = {path: sha256_file(path) for path in paths}
    grouped: dict[str, list[Path]] = defaultdict(list)
    for path, digest in hash_by_path.items():
        grouped[digest].append(path)

    records: list[SourceRecord] = []
    for path in paths:
        file_type = path.suffix.lower().lstrip(".")
        digest = hash_by_path[path]
        group_paths = sorted(grouped[digest], key=lambda item: str(item))
        canonical = path == group_paths[0]
        if file_type == "pdf":
            page_count = pdf_page_count(path)
            sample = pdf_sample_text(path)
        else:
            page_count = document_page_count(path)
            sample = document_sample_text(path)

        chars = text_char_count(sample)
        if chars >= 500:
            readability = "text_readable"
            confidence = "high"
        elif chars >= 80:
            readability = "text_readable_sparse"
            confidence = "medium"
        else:
            readability = "likely_ocr_or_conversion_needed"
            confidence = "low"

        rel_path = str(path)
        record = SourceRecord(
            source_id=f"src_{digest[:16]}",
            path=rel_path,
            file_name=path.name,
            file_type=file_type,
            sha256=digest,
            duplicate_group=f"dup_{digest[:12]}",
            canonical_source=canonical,
            apparent_role=classify_role(path),
            page_count=page_count,
            text_readability=readability,
            text_char_count_sample=chars,
            extraction_confidence=confidence,
            source_key=normalized_source_key(path),
            notes=compact_ws("exact duplicate" if len(group_paths) > 1 and not canonical else ""),
        )
        records.append(record)

    rows = [asdict(record) for record in records]
    write_jsonl(data_path("manifest", data_dir), rows)
    return rows
