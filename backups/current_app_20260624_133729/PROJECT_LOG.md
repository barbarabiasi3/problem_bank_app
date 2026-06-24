# MGT 404 Problem Bank App Log

Last updated: June 24, 2026

## Goal

Build a local-to-web teaching app for MGT 404 / Basics of Economics that:

- Ingests a local `problem_bank` folder containing PDFs, DOCX, and DOC files.
- Extracts problems and solutions into transparent local data files.
- Generates a large static practice bank for students.
- Serves a student-facing app where students choose a topic, generate one problem, and reveal the solution only after clicking.
- Lets students choose easy, medium, or hard practice problems on each topic page.
- Serves an instructor/admin app for inspection, disabling generated problems, and exporting the bank.
- Uses no hard-coded secrets and does not expose solutions in the initial student problem payload.

The final direction chosen in this session: no Gemini/live model calls for students. The deployed app should draw from the static generated bank only.

## Initial Inspection

The `problem_bank` folder was inspected and found to contain:

- 54 PDFs
- 90 DOCX files
- 2 DOC files
- Several spreadsheet/admin files that are ignored for extraction

All 54 PDFs appeared text-readable via `pdftotext`; no scan-only/OCR-required PDFs were detected. Some exact duplicate PDFs existed across archived folders, especially old 2018/2019 materials copied under 2020 folders. The extraction manifest hashes sources and marks canonical copies to avoid over-weighting duplicates.

The syllabus at `../MGT 404 (F26) Syllabus.docx` established the course topic spine:

- Supply and demand
- Equilibrium
- Elasticity
- Taxes and government intervention
- Trade policy
- Production and costs
- Perfect competition
- Monopoly
- Price discrimination
- Risk
- Adverse selection
- Moral hazard
- Game theory / strategic interaction

## Implemented Architecture

Framework:

- FastAPI backend
- Jinja2 server-rendered templates
- Plain CSS and vanilla JavaScript
- Uvicorn local server
- JSONL local data storage

Important files:

- `app/main.py`: FastAPI app, student/admin routes, JSONL data loading.
- `app/templates/`: Jinja templates.
- `app/static/styles.css`: Yale SOM-inspired visual design.
- `app/static/app.js`: student interaction, no-repeat client history, solution reveal.
- `problem_bank_tools/source_manifest.py`: source manifest builder.
- `problem_bank_tools/extraction.py`: source extraction and problem segmentation.
- `problem_bank_tools/verification.py`: optional Gemini-backed solution verification.
- `problem_bank_tools/generation.py`: optional Gemini-backed variant generation.
- `problem_bank_tools/seed_generation.py`: earlier deterministic test-bank generator.
- `problem_bank_tools/curated_bank.py`: current large local curated static bank generator.
- `scripts/*.py`: rerunnable pipeline commands.
- `data/*.jsonl`: transparent local data files.

## Data Files

Current data state:

- `data/source_manifest.jsonl`: 146 source records.
- `data/problems.jsonl`: 183 extracted original problems.
- `data/solutions.jsonl`: 183 extracted solution records.
- `data/audit_log.jsonl`: extraction/review notes.
- `data/generated_problems.jsonl`: 800 curated generated problems.

The generated bank has:

- 16 topics
- 50 generated problems per topic
- 15 easy, 25 medium, and 10 hard problems per topic
- 800 unique generated IDs
- 800 unique problem texts
- Matching `subparts` and `solution_subparts` labels for all generated records
- Exam-style prompts with 4 subparts for easy, 5 for medium, and 5-6 for hard

Current generated topics:

- Asymmetric Information
- Consumer Choice
- Elasticity
- Externalities and Public Goods
- Game Theory
- Incentives and Contracts
- Mixed Review
- Monopoly
- Oligopoly and Strategic Competition
- Perfect Competition
- Price Discrimination
- Production and Costs
- Risk and Insurance
- Supply and Demand
- Taxes and Government Intervention
- Trade and Welfare

## Major Design Decisions

Student side:

- Students see topic cards and total available problem counts only.
- Do not show generated/original split to students.
- Do not show source file, exam year, or any origin attribution to students.
- Student app samples from `data/generated_problems.jsonl` only.
- Students choose a difficulty level on each topic page; the default is medium.
- Extracted original problems remain available for admin/audit workflows but are not shown to students.
- The initial problem API response must not include `solution`, `given_solution`, or `verified_solution`.
- Solutions are fetched only after clicking `Show explained solution`.
- Solutions appear inline under each subpart in red.
- Each topic/difficulty avoids repeats in the browser until that topic/difficulty's available generated set is exhausted.
- After exhaustion, the topic/difficulty cycle resets but avoids immediately repeating the previous problem when possible.

Admin side:

- Shows source/problem/generated/audit summary.
- Can inspect generated variants and original extracted problems.
- Can disable/enable generated variants.
- Can export the JSONL bank as a zip.

Generation:

- The current production-like bank is local/static, not Gemini-generated.
- The command to rebuild it is:

```bash
python3 scripts/generate_curated_bank.py --per-topic 50
```

- The generated bank includes varied firm names, scenarios, wording, subpart prompts, parameters, and solution text.
- The June 24, 2026 refresh rewrote the generated bank in an exam-style structure inspired by past exams/problem sets and the local slide subset.
- Problems now include linked subquestions with calculation, interpretation, comparison, and policy/business reasoning instead of only short mechanical calculations.
- Repetitive wording was explicitly reduced. The generator should not stack an added scenario intro on top of a duplicated base setup.
- Fake but polished firm names are used, such as Aurora Scooters, BluePeak Batteries, Cobalt Cloud, Crimson Kite, Echo Forge, Flux Fitness, Halo Health, LoomLabs, Meridian Micro, Nebula Noodles, Nova Basket, Polaris Bikes, Prism Produce, Quantum Kettle, Sapphire Solar, Summit Seltzer, Vertex Coffee, Vanta Vacuum, Zenith Zips, and Atlas Droneworks.

Gemini:

- `.env.example` includes `GEMINI_API_KEY` and `GEMINI_MODEL`.
- Earlier plan allowed Gemini for offline verification/generation.
- Final user preference for this stage: forget Gemini and use a static locally generated bank.
- Gemini calls remain optional pipeline code, not required for the current app workflow.

## Visual Design Notes

The user requested an appearance inspired by a Yale School of Management lecture slide:

- White background
- Yale blue typography
- Top Yale SOM-like wordmark/header treatment
- Spacious but not oversized course-material style
- Restrained controls

Subsequent UI adjustments:

- Remove references to internal templates from student-facing titles.
- Use smaller titles and smaller fonts throughout.
- Reduce problem title font further.
- Add more spacing between the problem title and the first setup line.
- Keep solutions red and placed under each subpart.
- Remove the fake CSS Yale shield. The app now uses an official static logo asset if present and otherwise falls back to text-only branding.
- Add a compact difficulty selector to topic pages while keeping topic cards limited to total available problems.

Logo asset convention:

- Preferred: `app/static/img/yale-som-logo.svg`
- Also supported: `app/static/img/yale-som-logo.png`, `app/static/img/yale-logo.svg`, `app/static/img/yale-logo.png`

## Commands Used / Useful Commands

Install dependencies:

```bash
python3 -m pip install --user -r requirements.txt
```

Build source manifest:

```bash
python3 scripts/build_manifest.py
```

Extract source bank:

```bash
python3 scripts/extract_problem_bank.py
```

Generate current static curated bank:

```bash
python3 scripts/generate_curated_bank.py --per-topic 50
```

Run smoke tests:

```bash
python3 scripts/smoke_test.py
```

Run app:

```bash
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open app:

```bash
open http://127.0.0.1:8000
```

Important local URLs:

- Student app: `http://127.0.0.1:8000`
- Admin app: `http://127.0.0.1:8000/admin`
- Health check: `http://127.0.0.1:8000/health`

Recent backup:

- `backups/current_app_20260624_112258/` contains the pre-refresh app/code/data/docs/slides backup, excluding `.git`, existing backups, raw `problem_bank/`, cache dirs, and Finder metadata.

## Verification Performed

Repeated checks run during development:

- `python3 scripts/smoke_test.py`
- `python3 -m compileall problem_bank_tools scripts app`
- FastAPI `TestClient` checks for:
  - `/health`
  - `/`
  - `/admin`
  - `/api/problem`
  - `/api/problem?topic=...&difficulty=easy|medium|hard`
  - `/api/solution/...`
- Confirmed student problem payload does not include solution fields.
- Confirmed solution endpoint returns `solution_subparts`.
- Confirmed generated bank has 800 unique IDs and 800 unique problem texts.
- Confirmed all generated records align subparts and solution subparts.
- Confirmed every topic has 15 easy, 25 medium, and 10 hard generated problems.

## Current Running State

The local app was last restarted with:

```bash
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

At the time of this log, it was running on:

```text
http://127.0.0.1:8000
```

If browser CSS/JS seems stale, hard-refresh with `Cmd+Shift+R`.

## Remaining/Future Work

Potential next steps:

- Review sampled generated problems topic by topic for pedagogy and polish.
- Add richer admin filtering/search by topic, subtopic, and disabled status.
- Add persistent admin notes/flags beyond the current `disabled` field.
- Decide deployment target.
- Deploy with static `data/generated_problems.jsonl` bundled or mounted.
- Optionally remove unused Gemini paths if the app will permanently stay static-bank-only.
- Optionally add authentication to admin before publishing publicly.
