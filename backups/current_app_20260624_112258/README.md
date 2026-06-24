# MGT 404 Problem Bank App

This is a local-to-web practice problem app for MGT 404 / Basics of Economics. The student-facing app serves a static, curated generated problem bank from `data/generated_problems.jsonl`. Students do not call Gemini or any live model.

The app also includes instructor/admin tooling for inspecting extracted originals, generated variants, audit notes, disable/enable flags, and JSONL export.

## Current App Contract

Student-facing behavior:

- Samples only from `data/generated_problems.jsonl`.
- Keeps solutions out of the initial problem API payload.
- Reveals solutions only after `Show explained solution`.
- Displays solutions inline under each subpart.
- Avoids repeats within a topic until that topic is exhausted.
- Shows topic cards with total available problems only.
- Hides source filenames, exam names, years, and generated/original counts from students.

Generated records should include:

- `generated_id`
- `parent_problem_id`
- `topic`
- `subtopic`
- `difficulty`
- `problem_text`
- `subparts`
- `solution`
- `solution_subparts`
- `concepts_tested`
- `variation_notes`
- `parameters`
- `functions`
- `quality_checks`
- `disabled`
- `model`
- `created_at`

Every `subparts` item should have a matching `solution_subparts` item by label.

## Setup

```bash
python3 -m pip install -r requirements.txt
```

No API key is required to run the current student app. Optional Gemini scripts still exist for offline/admin experimentation, but they are not part of the student workflow.

## Run The App

```bash
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

Useful local URLs:

- Student app: `http://127.0.0.1:8000`
- Admin app: `http://127.0.0.1:8000/admin`
- Health check: `http://127.0.0.1:8000/health`

## Rebuild The Static Student Bank

```bash
python3 scripts/generate_curated_bank.py --per-topic 50
```

Expected current output:

- 800 generated problems
- 50 problems per topic
- 16 topics
- 800 unique generated IDs
- 800 unique problem texts
- 0 subpart/solution alignment issues

The generated bank is written to:

```text
data/generated_problems.jsonl
```

## QA

After changing app code or generation logic, run:

```bash
python3 scripts/smoke_test.py
python3 -m compileall problem_bank_tools scripts app
```

After changing generation logic, also run:

```bash
python3 - <<'PY'
from problem_bank_tools.utils import read_jsonl
rows = read_jsonl('data/generated_problems.jsonl')
print('rows', len(rows))
print('unique_ids', len({r['generated_id'] for r in rows}))
print('unique_texts', len({r['problem_text'] for r in rows}))
print('bad_alignment', sum(len(r.get('subparts', [])) != len(r.get('solution_subparts', [])) for r in rows))
PY
```

## Source Extraction Pipeline

Put source materials in:

```text
problem_bank/
```

The extraction pipeline reads `.pdf`, `.docx`, and `.doc` files. It ignores grade spreadsheets and other admin artifacts.

Build the source manifest:

```bash
python3 scripts/build_manifest.py
```

Extract problems and solutions:

```bash
python3 scripts/extract_problem_bank.py
```

Outputs:

- `data/source_manifest.jsonl`
- `data/problems.jsonl`
- `data/solutions.jsonl`
- `data/audit_log.jsonl`

Extracted originals are for instructor/admin review and audit. They are not shown in the student app.

## Optional Gemini Tools

Gemini support remains in optional scripts and modules:

- `problem_bank_tools/gemini_client.py`
- `problem_bank_tools/verification.py`
- `problem_bank_tools/generation.py`
- `scripts/verify_solutions.py`
- `scripts/generate_variants.py`

If using those optional tools, keep API keys server-side or local-only. Do not reintroduce live Gemini/model calls into the student workflow unless that product direction changes.

## Deployment Notes

For a simple deployment:

1. Deploy the FastAPI app with `uvicorn` or `gunicorn` plus a Uvicorn worker.
2. Bundle or mount the `data/` directory, especially `data/generated_problems.jsonl`.
3. Do not require Gemini credentials for the student app.
4. Add admin authentication before making `/admin` internet-accessible.
5. Keep generated-bank rebuilds as offline/local maintenance work.

## Design Notes

The student UI should feel like Yale SOM course material: white background, Yale blue typography, restrained controls, smaller readable fonts, and no decorative gradient/orb treatment. Use an official supplied Yale/Yale SOM logo asset only; otherwise the header falls back to text branding.

Logo asset convention:

- Preferred: `app/static/img/yale-som-logo.svg`
- Also supported: `app/static/img/yale-som-logo.png`, `app/static/img/yale-logo.svg`, `app/static/img/yale-logo.png`

## Project Notes

- Original source files are never overwritten.
- Exact duplicate source files are grouped by hash and only canonical copies are extracted.
- Admin may show source counts, audit notes, extracted originals, generated variants, disable/enable controls, and export.
- Student-facing text should not use internal words like `template`.
