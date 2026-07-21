# Judge testing guide

TraceLog has two intentionally separate testing paths. The offline fixture makes the product
experience easy to inspect; only the live path demonstrates GPT-5.6 and Phoenix execution.

## Path A — offline fixture (no credentials)

Requirements: Python 3.11+ and Node.js 22+.

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
npm --prefix web ci
npm --prefix web run build
cp .env.example .env
```

Set this single value in `.env`:

```env
OFFLINE_DEMO_MODE=true
```

Start the cockpit:

```bash
.venv/bin/uvicorn dashboard.main:app --port 8085
```

Open `http://localhost:8085` and click **Play offline fixture**. The cockpit replays all nine
stages through its SSE feed. A persistent banner states that the artifacts are deterministic
fixtures and that no OpenAI or Phoenix calls were made.

Expected health response:

```json
{"ok":true,"service":"dashboard","ui":true,"mode":"offline_fixture"}
```

## Path B — live GPT-5.6 + Phoenix

Set `OFFLINE_DEMO_MODE=false`, then provide a funded OpenAI API key, the full Phoenix space
URL, and a Phoenix system API key. Never commit these values.

```env
OPENAI_API_KEY=...
PHOENIX_BASE_URL=https://app.phoenix.arize.com/s/YOUR-SPACE
PHOENIX_API_KEY=...
STATE_BACKEND=local
PATIENT_ENDPOINT=http://localhost:8082/chat
OFFLINE_DEMO_MODE=false
```

Start the two services in separate terminals and run one supervision cycle:

```bash
.venv/bin/uvicorn patient.agent:app --port 8082
.venv/bin/uvicorn dashboard.main:app --port 8085
.venv/bin/python scripts/run_pipeline.py
```

The live acceptance is successful only when Phoenix contains the Patient trace and TraceLog
annotation, the cockpit reaches `red_teamed`, and `reports/<incident-id>.md` exists. A valid
API key without available quota returns `429 insufficient_quota` and does not count as a
successful live run.

## Automated verification

```bash
.venv/bin/pytest -q
.venv/bin/ruff check tracelog patient dashboard tests
.venv/bin/mypy --ignore-missing-imports tracelog patient dashboard
npm --prefix web ci
npm --prefix web run build
npm --prefix web audit --omit=dev --audit-level=high
```
