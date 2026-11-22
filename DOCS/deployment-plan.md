# Deployment Plan — Vercel (Frontend) + Railway (Backend)

Plan to host the Next.js UI on **Vercel** and the FastAPI recommender on **Railway**, using free tiers where possible.

Aligned with current layout: [`web/`](../web/) (Next.js) + [`src/api/main.py`](../src/api/main.py) (FastAPI).

---

## Target architecture

```
User browser
     │
     ▼
┌─────────────────┐     NEXT_PUBLIC_API_URL      ┌──────────────────────┐
│  Vercel         │ ───────────────────────────► │  Railway             │
│  Next.js (web/) │     HTTPS JSON               │  FastAPI + uvicorn     │
└─────────────────┘                              │  RestaurantStore     │
                                                 │  Groq / Mock LLM     │
                                                 └──────────────────────┘
```

| Layer | Service | Free-tier notes |
|---|---|---|
| Frontend | Vercel Hobby | Generous for static/SSR hobby apps; custom domain optional |
| Backend | Railway trial / free credits | Sleeps when idle on some plans; cold starts possible; watch RAM for dataset load |
| LLM | Groq free tier | Rate limits apply; set `USE_MOCK_LLM=true` for demos without a key |

---

## Prerequisites

1. GitHub (or GitLab/Bitbucket) repo with this project pushed  
2. Accounts: [Vercel](https://vercel.com), [Railway](https://railway.app), optional [Groq](https://console.groq.com/keys)  
3. Local smoke test still works:
   - API: `uvicorn src.api.main:app --port 8000`
   - Web: `cd web && npm run dev`

---

## Phase 0 — Pre-deploy code changes (required)

Do these in the repo **before** first production deploy.

### 0.1 CORS for the Vercel origin

[`src/api/main.py`](../src/api/main.py) currently allows only `localhost:3000`. Change to env-driven origins, for example:

- `CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000`
- Parse comma-separated list in FastAPI `CORSMiddleware`

Without this, the browser will block `/meta` and `/recommend` from Vercel.

### 0.2 Dataset on Railway

The store prefers local parquet at `DATA_CACHE_PATH` (`data/restaurants.parquet`). On Railway either:

| Option | Pros | Cons |
|---|---|---|
| **A. Commit or bake parquet into the image** (preferred for demo) | Fast cold start; no HF download | Repo/image size; ensure `data/*.parquet` is not gitignored for deploy branch or use a Railway volume / build step that copies cache |
| **B. Load from Hugging Face on first boot** | No large binary in git | Slow first request; needs network; may OOM on tiny free instances |

Recommendation for free demo: ship parquet via a build step or Railway volume; keep `DATA_CACHE_PATH=data/restaurants.parquet`.

### 0.3 Bind host / port for Railway

Railway injects `PORT`. Start command must use it:

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
```

### 0.4 Frontend API URL

Set `NEXT_PUBLIC_API_URL` to the public Railway HTTPS URL (no trailing slash), e.g. `https://food-api-production.up.railway.app`.

This must be present at **Vercel build time** (Next inlines `NEXT_PUBLIC_*`).

### 0.5 Optional hardening

- Health check path: `/health` (already exists)  
- Trim Streamlit from Railway image if building a slim `requirements-api.txt` (fastapi, uvicorn, pandas, pyarrow, groq, pydantic, python-dotenv, datasets only if HF load is needed)  
- Do **not** put `GROQ_API_KEY` in the frontend  

---

## Phase 1 — Deploy backend on Railway

### 1.1 Create service

1. New project → **Deploy from GitHub** → select this repo  
2. Root directory: **repository root** (not `web/`)  
3. Railway should detect Python; if not, set manually

### 1.2 Build & start

Suggested settings:

| Setting | Value |
|---|---|
| Build | `pip install -r requirements.txt` (or `requirements-api.txt` if you split deps) |
| Start | `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT` |
| Watch paths | `src/**`, `data/**`, `requirements.txt` |

### 1.3 Environment variables (Railway)

| Variable | Example / notes |
|---|---|
| `GROQ_API_KEY` | From Groq console (omit if mock) |
| `USE_MOCK_LLM` | `false` for live; `true` for offline demo |
| `LLM_PROVIDER` | `groq` |
| `LLM_MODEL` | `openai/gpt-oss-20b` |
| `LLM_TEMPERATURE` | `0.2` |
| `LLM_BASE_URL` | `https://api.groq.com/openai/v1` |
| `TOP_K` | `5` |
| `MAX_CANDIDATES` | `25` |
| `DATA_CACHE_PATH` | `data/restaurants.parquet` |
| `CORS_ORIGINS` | `https://<your-vercel-app>.vercel.app,http://localhost:3000` |
| `HF_DATASET_ID` | Only needed if falling back to HF load |
| `HF_DATASET_SPLIT` | `train` |

Update `CORS_ORIGINS` again after the Vercel URL is known (or use a preview + production pair).

### 1.4 Networking

1. Generate a **public HTTPS domain** in Railway  
2. Confirm: `GET https://<railway-host>/health` → `{"status":"ok"}`  
3. Confirm: `GET https://<railway-host>/meta` returns locations + `restaurant_count`  
4. Optional: `POST /recommend` with a small JSON body from curl / Railway logs

### 1.5 Free-tier watchouts

- Cold start after idle: first `/meta` or `/recommend` may take longer while the store loads  
- Memory: 12k+ row parquet + pandas — prefer 512MB+ if the free plan allows; if OOM, use mock + smaller cache or HF sample  
- Sleeping services: wake on first request; UI should show a loading / “waking API” state  

---

## Phase 2 — Deploy frontend on Vercel

### 2.1 Import project

1. Vercel → **Add New Project** → import the same GitHub repo  
2. Configure:

| Setting | Value |
|---|---|
| Framework | Next.js |
| Root Directory | `web` |
| Build Command | `npm run build` (default) |
| Output | Next default (no change) |
| Install | `npm install` |

### 2.2 Environment variables (Vercel)

| Variable | Value | Scope |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `https://<railway-host>` (no trailing slash) | Production (+ Preview if API allows preview CORS) |

Redeploy after changing `NEXT_PUBLIC_*` so the client bundle picks it up.

### 2.3 Domains

1. Use the default `*.vercel.app` URL first  
2. Add that exact origin to Railway `CORS_ORIGINS`  
3. Optional later: custom domain on Vercel; add it to CORS as well  

### 2.4 Verify

1. Open the Vercel URL  
2. Mode chip loads (calls `/meta`)  
3. Submit preferences → recommendations or friendly empty/error cards  
4. Browser DevTools → Network: `/meta` and `/recommend` return 200 (not CORS / failed fetch)

---

## Phase 3 — Wire-up checklist (order matters)

```
1. Push CORS + PORT-ready API changes
2. Deploy Railway → copy public URL
3. Set Vercel NEXT_PUBLIC_API_URL → deploy web/
4. Set Railway CORS_ORIGINS to Vercel URL → redeploy API if needed
5. End-to-end test on production URLs
```

---

## Phase 4 — Post-deploy validation

| Check | Pass criteria |
|---|---|
| API health | `/health` 200 |
| Meta | `/meta` returns ~12k count (or known cache size) |
| UI boot | Preferences + location list render |
| Happy path | Recommend returns grounded cards |
| Empty path | Over-strict filters → empty state message |
| Auth path | Missing Groq key + `USE_MOCK_LLM=false` → clear API key error |
| CORS | No browser CORS errors on Vercel origin |
| Mobile | Form + cards usable on narrow viewport |

---

## Suggested repo extras (optional but useful)

| File | Purpose |
|---|---|
| `Procfile` or Railway start command | `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT` |
| `runtime.txt` / `Python` version pin | Match local 3.11+ if Railway auto-detect drifts |
| `requirements-api.txt` | Slimmer image without Streamlit |
| `vercel.json` | Only if you need rewrites/headers; not required for standard Next |
| GitHub Actions | Optional CI: `pytest` + `npm run build` on PR |

---

## Cost & limits (free path)

- **Vercel Hobby:** fine for a portfolio/demo frontend  
- **Railway:** use trial credits carefully; expect sleep/cold start; upgrade only if demos must stay warm  
- **Groq:** free quota is enough for light demos; fall back to `USE_MOCK_LLM=true` for workshops  

---

## Rollback

1. Vercel → previous Deployment → Promote  
2. Railway → previous successful deploy  
3. Keep `USE_MOCK_LLM=true` as emergency mode if Groq is down  

---

## Definition of done

- [ ] API public on Railway; `/health` and `/meta` OK  
- [ ] Next.js public on Vercel; talks to Railway via `NEXT_PUBLIC_API_URL`  
- [ ] CORS allows the Vercel origin  
- [ ] Live or mock LLM path works end-to-end  
- [ ] README (or this doc) lists production URLs and env vars for the team  

---

## Related docs

- [`architecture.md`](./architecture.md) — system design  
- [`implementation-plan.md`](./implementation-plan.md) — build phases  
- [`../README.md`](../README.md) — local run instructions  
