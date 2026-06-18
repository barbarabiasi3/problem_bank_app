# MGT 404 Problem Bank App

This project builds a local-to-web problem-bank system for MGT 404 / Basics of Economics. It ingests source PDFs and Word documents from `problem_bank`, extracts structured problems and provided solutions, supports Gemini-based solution verification and variant generation, and serves a student/admin web app.

## Setup

```bash
python3 -m pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and add your own Gemini key:

```bash
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.5-flash
```

The API key is read server-side only. It is never sent to the browser.

## Source Folder

Put input materials in:

```bash
problem_bank/
```

The current pipeline reads `.pdf`, `.docx`, and `.doc` files. It ignores grade spreadsheets and other admin artifacts. PDFs are preferred for page traceability; Word files are used as supplementary sources when they contain newer or clearer material.

## Stage 1: Build Manifest

```bash
python3 scripts/build_manifest.py
```

Output:

```bash
data/source_manifest.jsonl
```

Each source record includes path, file type, SHA-256 hash, duplicate group, canonical-source flag, apparent role, page count, text readability, extraction confidence, and normalized source key.

## Stage 2: Extract Problems And Solutions

```bash
python3 scripts/extract_problem_bank.py
```

Outputs:

```bash
data/problems.jsonl
data/solutions.jsonl
data/audit_log.jsonl
```

Uncertain extractions are preserved and logged rather than discarded. Every problem record keeps source traceability, including source file and PDF page range where available.

## Stage 3: Verify Solutions

Run a small batch first:

```bash
python3 scripts/verify_solutions.py --limit 10
```

Then continue in larger batches:

```bash
python3 scripts/verify_solutions.py --limit 50
```

The verifier independently asks Gemini to solve/check each extracted problem and classify the solution as `correct`, `minor_issue`, `incorrect`, `incomplete`, or `unknown`. Non-correct or ambiguous items receive audit notes and a corrected/explained solution when Gemini can provide one.

## Stage 4: Generate Variants

Generate in small batches. Example:

```bash
python3 scripts/generate_variants.py --topic "Supply and Demand" --parent-limit 1 --per-parent 5
```

Full target generation for reviewed parents:

```bash
python3 scripts/generate_variants.py --per-parent 50 --batch-size 5
```

By default, generation uses only parents marked `correct` or `minor_issue`. Use `--allow-unknown` only for early prototyping, not for production teaching materials.

Output:

```bash
data/generated_problems.jsonl
```

Each generated item stores parent traceability, solution, concepts, variation notes, parameters/functions, quality checks, model, timestamp, and `disabled` status.

## Stage 5: Run The App

```bash
uvicorn app.main:app --reload
```

Open:

```bash
http://127.0.0.1:8000
```

Student flow:

1. Select a topic.
2. Click `Generate problem`.
3. Read the problem without seeing the solution.
4. Click `Show explained solution`.
5. Generate another problem on the same topic.

Admin flow:

```bash
http://127.0.0.1:8000/admin
```

From the admin page you can inspect topics, original problems, generated variants, recent audit notes, disable/enable generated variants, and export the full JSONL bank as a zip.

## Deployment

Recommended simple deployment:

1. Deploy the FastAPI app with `uvicorn` or `gunicorn` plus `uvicorn-worker`.
2. Set `GEMINI_API_KEY` and `GEMINI_MODEL` as server environment variables.
3. Keep Gemini calls server-side only.
4. Pre-generate and verify most variants offline.
5. Serve students from `data/generated_problems.jsonl`; use live generation only in admin workflows.

For a lightweight hosted setup, a small VM or Render/Fly.io-style Python web service is enough. Keep `data/` mounted as persistent storage if you want admin disable flags and generated variants to survive redeploys.

## QA

Run the local smoke test after extraction:

```bash
python3 scripts/smoke_test.py
```

The smoke test checks that required JSONL files exist, problems and solutions line up, required fields are present, statuses are valid, and generated problem text does not contain obvious answer markers.

## Notes

- Original files are never overwritten.
- Exact duplicate source files are grouped by hash and only the first canonical copy is extracted.
- Solutions are never included in the student problem endpoint; they are fetched only after `Show explained solution`.
- The attached Yale SOM slide guided the visual style: white page, Yale blue typography, large lecture-style headings, and restrained controls.
