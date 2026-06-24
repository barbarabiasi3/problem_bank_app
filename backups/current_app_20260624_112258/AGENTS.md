# AGENTS.md

Instructions for future agents working in this repository.

## Project Purpose

This is a local-to-web MGT 404 / Basics of Economics practice problem app for a university instructor. The student-facing app should serve a static, curated generated problem bank. Students should not call Gemini or any live model. Students should draw from the bank only.

## Current Architecture

- Framework: FastAPI
- Templates: Jinja2
- Frontend: plain CSS and vanilla JavaScript
- Data: JSONL files under `data/`
- Server: Uvicorn

Key files:

- `app/main.py`: FastAPI routes and app data access.
- `app/templates/`: student/admin HTML templates.
- `app/static/styles.css`: Yale SOM-inspired styling.
- `app/static/app.js`: client-side generate/show-solution behavior.
- `problem_bank_tools/curated_bank.py`: current static-bank generator.
- `scripts/generate_curated_bank.py`: command wrapper for curated-bank generation.
- `data/generated_problems.jsonl`: static generated bank used by students.

## Current Data Contract

Student-facing generated records live in `data/generated_problems.jsonl`.

Each generated record should include:

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

Every `subparts` item must have a matching `solution_subparts` item by label. The app displays solutions inline in red under each subpart.

## Student App Rules

Do:

- Sample from `data/generated_problems.jsonl` only.
- Hide solutions until the student clicks `Show explained solution`.
- Keep solutions out of the initial problem API payload.
- Display solutions inline under each subpart in red.
- Avoid repeats within a topic until the topic is exhausted.
- Show only total available problems on topic cards.
- Keep wording clean and student-facing.

Do not:

- Show source file names, original exam names, years, or source attribution to students.
- Show "generated vs original" counts to students.
- Fall back to extracted original exam/problem-set records on the student side.
- Expose API keys or live model calls in the browser.
- Use Gemini/live generation for students.
- Include internal words like "template" in student-facing titles.

## Admin App Rules

The admin side may show extracted originals, generated variants, source counts, audit notes, disable/enable controls, and export.

Before public deployment, add admin authentication if the admin route will be internet-accessible.

## Visual Design Preferences

The UI should feel like a Yale SOM lecture-slide/course-material interface:

- White background
- Yale blue typography
- Clean top Yale SOM-like wordmark/header
- Restrained controls
- Smaller, readable fonts rather than oversized marketing typography
- No decorative gradient blobs/orbs
- No generic landing-page hero treatment

Recent visual decisions:

- Titles should be smaller than the first implementation.
- Problem title should have extra spacing before the first setup line.
- Topic cards should show total available problems only.
- Solutions should appear in red under each subpart.
- Do not use a fake Yale shield. The header renders an official static logo file if present, otherwise it falls back to text-only.

Logo asset convention:

- Preferred file: `app/static/img/yale-som-logo.svg`
- Also supported: `app/static/img/yale-som-logo.png`, `app/static/img/yale-logo.svg`, `app/static/img/yale-logo.png`
- Use only official Yale/Yale SOM assets supplied by the instructor or downloaded from Yale Identity with appropriate access/permission.

## Generation Guidance

The current generator is local/static:

```bash
python3 scripts/generate_curated_bank.py --per-topic 50
```

It currently produces:

- 800 generated problems
- 50 per topic
- 16 topics
- 800 unique IDs
- 800 unique problem texts

If modifying the generator:

- Preserve mathematical correctness.
- Keep solutions aligned with subparts.
- Avoid merely changing numbers.
- Vary scenario, wording, subpart prompts, and qualitative framing.
- Avoid repetitive wording where an intro repeats the same setup sentence.
- Use polished fake firm names.
- Keep questions at intermediate microeconomics level.
- Avoid pathological values unless explicitly teaching a corner case.

After modifying generation, run:

```bash
python3 scripts/generate_curated_bank.py --per-topic 50
python3 scripts/smoke_test.py
python3 -m compileall problem_bank_tools scripts app
```

Also run a duplicate check:

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

All four numbers should be healthy. At the time this file was written:

- rows: 800
- unique_ids: 800
- unique_texts: 800
- bad_alignment: 0

## Useful Commands

Run the app:

```bash
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open the app:

```bash
open http://127.0.0.1:8000
```

Run extraction pipeline:

```bash
python3 scripts/build_manifest.py
python3 scripts/extract_problem_bank.py
```

Run smoke test:

```bash
python3 scripts/smoke_test.py
```

## Current Source/Data Counts

At the time this file was written:

- `data/source_manifest.jsonl`: 146 records
- `data/problems.jsonl`: 183 extracted original problems
- `data/solutions.jsonl`: 183 solution records
- `data/generated_problems.jsonl`: 800 generated problems

## Notes About Gemini

Gemini support exists in optional files:

- `problem_bank_tools/gemini_client.py`
- `problem_bank_tools/verification.py`
- `problem_bank_tools/generation.py`
- `scripts/verify_solutions.py`
- `scripts/generate_variants.py`

However, the user explicitly chose the static local-bank direction for publishing. Do not reintroduce Gemini/live calls into the student workflow unless the user asks for that again.
