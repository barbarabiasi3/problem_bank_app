from __future__ import annotations

import io
import os
import random
import zipfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from problem_bank_tools.utils import DATA_FILES, compact_ws, read_jsonl, slugify, write_jsonl


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("PROBLEM_BANK_DATA_DIR", PROJECT_ROOT / "data"))

app = FastAPI(title="MGT 404 Problem Bank")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


def _jsonl(name: str) -> Path:
    return DATA_DIR / DATA_FILES[name]


def load_rows(name: str) -> list[dict[str, Any]]:
    return read_jsonl(_jsonl(name))


def save_rows(name: str, rows: list[dict[str, Any]]) -> None:
    write_jsonl(_jsonl(name), rows)


def load_bank() -> dict[str, list[dict[str, Any]]]:
    return {
        "manifest": load_rows("manifest"),
        "problems": load_rows("problems"),
        "solutions": load_rows("solutions"),
        "generated": load_rows("generated"),
        "audit": load_rows("audit"),
    }


def topic_summary() -> list[dict[str, Any]]:
    bank = load_bank()
    topics: dict[str, dict[str, Any]] = {}
    for problem in bank["problems"]:
        topic = problem.get("topic") or "Unclassified"
        topics.setdefault(topic, {"topic": topic, "slug": slugify(topic), "originals": 0, "generated": 0})
        topics[topic]["originals"] += 1
    for generated in bank["generated"]:
        if generated.get("disabled"):
            continue
        topic = generated.get("topic") or "Unclassified"
        topics.setdefault(topic, {"topic": topic, "slug": slugify(topic), "originals": 0, "generated": 0})
        topics[topic]["generated"] += 1
    return sorted(topics.values(), key=lambda item: item["topic"])


def topic_from_slug(topic_slug: str) -> str:
    for topic in topic_summary():
        if topic["slug"] == topic_slug:
            return topic["topic"]
    raise HTTPException(status_code=404, detail="Topic not found")


def active_items_for_topic(topic: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    bank = load_bank()
    generated = [
        row
        for row in bank["generated"]
        if row.get("topic") == topic and not row.get("disabled") and row.get("problem_text")
    ]
    originals = [
        row
        for row in bank["problems"]
        if row.get("topic") == topic and row.get("problem_text")
    ]
    return generated, originals


def find_problem(item_type: str, item_id: str) -> dict[str, Any]:
    name = "generated" if item_type == "generated" else "problems"
    id_key = "generated_id" if item_type == "generated" else "problem_id"
    for row in load_rows(name):
        if row.get(id_key) == item_id:
            return row
    raise HTTPException(status_code=404, detail="Problem not found")


def public_problem_payload(item_type: str, row: dict[str, Any]) -> dict[str, Any]:
    item_id = row["generated_id"] if item_type == "generated" else row["problem_id"]
    return {
        "item_type": item_type,
        "item_id": item_id,
        "topic": row.get("topic", "Unclassified"),
        "subtopic": row.get("subtopic", ""),
        "difficulty": row.get("difficulty", "medium"),
        "problem_title": row.get("problem_title") or row.get("variation_notes", ""),
        "problem_text": row.get("problem_text", ""),
        "subparts": row.get("subparts", []),
        "source_file": row.get("source_file", ""),
        "solution_url": f"/api/solution/{item_type}/{item_id}",
    }


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "topics": topic_summary()},
    )


@app.get("/topic/{topic_slug}", response_class=HTMLResponse)
def topic_page(request: Request, topic_slug: str) -> HTMLResponse:
    topic = topic_from_slug(topic_slug)
    generated, originals = active_items_for_topic(topic)
    return templates.TemplateResponse(
        "topic.html",
        {
            "request": request,
            "topic": topic,
            "topic_slug": topic_slug,
            "generated_count": len(generated),
            "original_count": len(originals),
        },
    )


@app.get("/api/problem")
def api_problem(topic: str) -> dict[str, Any]:
    generated, originals = active_items_for_topic(topic)
    if generated:
        row = random.choice(generated)
        return public_problem_payload("generated", row)
    if originals:
        row = random.choice(originals)
        return public_problem_payload("original", row)
    raise HTTPException(status_code=404, detail="No active problems for this topic")


@app.get("/api/solution/{item_type}/{item_id}")
def api_solution(item_type: str, item_id: str) -> dict[str, Any]:
    if item_type not in {"generated", "original"}:
        raise HTTPException(status_code=404, detail="Unknown problem type")
    row = find_problem(item_type, item_id)
    if item_type == "generated":
        solution = row.get("solution", "")
        status = "generated_verified" if solution else "missing"
    else:
        solution = row.get("verified_solution") or row.get("given_solution") or ""
        status = row.get("solution_status", "unknown")
    if not solution:
        solution = "No verified solution is available yet. Use the admin workflow to verify or regenerate this item."
    return {"item_type": item_type, "item_id": item_id, "solution_status": status, "solution": solution}


@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request) -> HTMLResponse:
    bank = load_bank()
    generated = bank["generated"]
    disabled_generated = sum(1 for row in generated if row.get("disabled"))
    unverified = sum(1 for row in bank["problems"] if row.get("solution_status") == "unknown")
    source_roles: dict[str, int] = {}
    for source in bank["manifest"]:
        source_roles[source.get("apparent_role", "unknown")] = source_roles.get(source.get("apparent_role", "unknown"), 0) + 1
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "topics": topic_summary(),
            "source_count": len(bank["manifest"]),
            "problem_count": len(bank["problems"]),
            "generated_count": len(generated),
            "disabled_generated": disabled_generated,
            "unverified_count": unverified,
            "source_roles": source_roles,
            "generated": generated[:200],
            "problems": bank["problems"][:200],
            "audit": list(reversed(bank["audit"]))[:40],
            "gemini_model": os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
            "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        },
    )


@app.post("/admin/generated/{generated_id}/toggle")
def toggle_generated(generated_id: str, disabled: bool = False) -> RedirectResponse:
    rows = load_rows("generated")
    found = False
    for row in rows:
        if row.get("generated_id") == generated_id:
            row["disabled"] = disabled
            found = True
            break
    if not found:
        raise HTTPException(status_code=404, detail="Generated problem not found")
    save_rows("generated", rows)
    return RedirectResponse("/admin", status_code=303)


@app.get("/admin/export")
def export_bank() -> Response:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_name in DATA_FILES.values():
            path = DATA_DIR / file_name
            if path.exists():
                archive.write(path, arcname=file_name)
    buffer.seek(0)
    return Response(
        content=buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="mgt404_problem_bank_export.zip"'},
    )


@app.get("/health")
def health() -> dict[str, Any]:
    bank = load_bank()
    return {
        "status": "ok",
        "sources": len(bank["manifest"]),
        "problems": len(bank["problems"]),
        "generated": len(bank["generated"]),
        "topics": len(topic_summary()),
        "data_dir": str(DATA_DIR),
    }


templates.env.filters["compact"] = compact_ws
templates.env.filters["slugify"] = slugify
