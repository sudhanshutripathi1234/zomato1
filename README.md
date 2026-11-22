# AI-Powered Restaurant Recommendation System

Zomato-inspired recommendations: filter a real restaurant dataset, then use an LLM to rank and explain grounded candidates.

**Primary UI:** Next.js (Stitch dark theme) + FastAPI  
**Optional demo:** Streamlit

## Quick start

```bash
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
copy .env.example .env
```

Edit `.env`:

- Offline demo (no API key): `USE_MOCK_LLM=true`
- Live Groq ranking: set `GROQ_API_KEY` from [Groq Console](https://console.groq.com/keys) and `USE_MOCK_LLM=false`

### 1. Start the API

```bash
uvicorn src.api.main:app --reload --port 8000
```

- Health: http://localhost:8000/health  
- Docs: http://localhost:8000/docs  

### 2. Start the Next.js UI

```bash
cd web
copy .env.local.example .env.local
npm install
npm run dev
```

Open **http://localhost:3000**

1. Pick location, budget, cuisine, min rating, and optional extras  
2. Submit → loading state while filters + LLM run  
3. See ranked cards with name, cuisine, rating, cost, and AI explanation  

`NEXT_PUBLIC_API_URL` in `web/.env.local` should point at the API (`http://localhost:8000`).

### Optional: Streamlit demo

```bash
streamlit run src/app.py
```

### Demo checklist

- [ ] API starts and `/meta` returns locations + restaurant count
- [ ] Next UI loads preferences and mode chip
- [ ] Empty filters show a clear “relax filters” message (no crash)
- [ ] Mock mode returns grounded Top-K offline
- [ ] With `GROQ_API_KEY`, live mode ranks/explains candidates
- [ ] Missing API key (live mode) shows a friendly setup message

## Deploy (Vercel + Railway)

Full steps: [DOCS/deployment-plan.md](DOCS/deployment-plan.md).

**Railway (API)** — root of repo, uses `requirements-api.txt` + `railway.toml`:

- Start: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
- Set env: `GROQ_API_KEY`, `USE_MOCK_LLM`, `CORS_ORIGINS=https://<vercel-app>.vercel.app,http://localhost:3000`, `DATA_CACHE_PATH=data/restaurants.parquet`
- Ship `data/restaurants.parquet` with the repo for fast cold starts

**Vercel (UI)** — Root Directory = `web`:

- Env: `NEXT_PUBLIC_API_URL=https://<railway-host>` (no trailing slash; set before build)
- After Vercel URL exists, update Railway `CORS_ORIGINS` and redeploy the API

## CLI / tests

```bash
# Phase 1 — data
python scripts/inspect_data.py

# Phase 2 — filters
pytest tests/test_filters.py
python scripts/filter_demo.py

# Phase 3 — LLM recommend
pytest tests/test_llm_parser.py tests/test_recommender.py
python scripts/recommend_demo.py

# Full unit/integration suite
pytest tests/
```

Default Groq model: `openai/gpt-oss-20b`. Hallucinated restaurant ids are dropped; parse failures retry once, then fall back to rating sort.

## Project layout

```
FOOD/
├── DOCS/                 # product + architecture docs
├── data/                 # restaurants.parquet (tracked for Railway)
├── scripts/              # utility / demo scripts
├── src/
│   ├── api/              # FastAPI (/health, /meta, /recommend)
│   ├── app.py            # optional Streamlit UI
│   ├── config.py
│   ├── data/             # loader + store
│   ├── llm/              # client + parser
│   ├── models/           # prefs + response DTOs
│   └── services/         # filters, prompts, orchestrator
├── web/                  # Next.js App Router frontend (Vercel root)
├── tests/
├── Procfile / railway.toml / nixpacks.toml / runtime.txt
├── .env.example
├── requirements.txt      # local full deps
└── requirements-api.txt  # Railway slim deps
```

## Docs

- [Problem statement](DOCS/pstatement.md)
- [Architecture](DOCS/architecture.md)
- [Implementation plan](DOCS/implementation-plan.md)
- [Edge cases](DOCS/edge-case.md)
- [Data notes](DOCS/data-notes.md)
- [Deployment plan](DOCS/deployment-plan.md)
