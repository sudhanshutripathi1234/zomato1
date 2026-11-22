# Implementation Plan — AI-Powered Restaurant Recommendation System

Phase-wise plan to build the system described in [`pstatement.md`](./pstatement.md) and [`architecture.md`](./architecture.md).

**Approach:** filter first, then LLM rank/explain; ship mock LLM early so UI work is not blocked on API keys.

---

## Overview

| Phase | Name | Goal |
|---|---|---|
| 1 | Foundation & data | Repo setup + load/normalize HF dataset into a store |
| 2 | Candidate retrieval | Prefs, hard filters, soft scoring, candidate capping |
| 3 | LLM recommendations | Prompting, LLM client, parsing, full orchestrator |
| 4 | UI & hardening | Streamlit UI, tests, docs, demo-ready v1 |

```
Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4
```

---

## Phase 1 — Foundation & data

**Goal:** Runnable project skeleton and a cached, queryable restaurant store from Hugging Face.

### Tasks

- [x] Create folder layout (`src/`, `tests/`, `data/`, `DOCS/`)
- [x] Add `requirements.txt`, `.env.example`, `src/config.py`, minimal README
- [x] Inspect HF dataset schema (`ManikaSaini/zomato-restaurant-recommendation`)
- [x] Implement `loader.py`: load, clean, normalize cuisine/rating/cost, assign `restaurant_id`, derive `budget_band`
- [x] Implement `store.py`: load-once cache, list / get-by-id
- [x] Optional: local parquet/CSV snapshot under `data/`

### Exit criteria

- [x] Fresh setup installs deps and loads config from `.env`
- [x] Dataset loads once; can print row counts, sample locations/cuisines, cost/rating ranges

See also: [`data-notes.md`](./data-notes.md), `scripts/inspect_data.py`

---

## Phase 2 — Candidate retrieval

**Goal:** Turn user preferences into a deterministic, capped shortlist (no LLM yet).

### Tasks

- [x] Define models: PreferenceInput, Restaurant, response stubs
- [x] Validate prefs (budget enum, rating bounds, `top_k`, free-text length)
- [x] Hard filters: location, cuisine, min rating, budget → cost range
- [x] Soft scoring from additional prefs (family-friendly, quick service, etc.)
- [x] Sort (soft score → rating) and cap to `max_candidates` (15–30)
- [x] Return meta (`filters_applied`, `candidate_count`)
- [x] Unit tests for budget mapping, filters, empty results, cap size

### Exit criteria

- [x] Known prefs → correct, deterministic shortlist
- [x] Empty matches return `[]` without crashing; shortlist never exceeds cap

Run: `pytest tests/test_filters.py` · demo: `python scripts/filter_demo.py`

---

## Phase 3 — LLM recommendations

**Goal:** End-to-end `recommend(prefs)` that ranks candidates and explains fits, grounded by `restaurant_id`.

### Tasks

- [x] `LLMClient` interface + **Groq** provider + **mock client** for offline work
- [x] Prompt builder: rank only from candidates; JSON output; no invented facts
- [x] Parser: extract/validate JSON; drop unknown ids
- [x] Orchestrator (`recommender.py`): validate → filter/cap → prompt → LLM → join metadata → Top-K DTO
- [x] Empty candidates skip LLM; parse failure → one retry → rating-sorted fallback
- [x] Integration test with fixture store + mock LLM

### Exit criteria

- [x] Mock path works offline and returns grounded Top-K
- [x] Hallucinated restaurant ids never appear in the final response

Run: `pytest tests/test_llm_parser.py tests/test_recommender.py` · demo: `python scripts/recommend_demo.py`  
Set `GROQ_API_KEY` and `USE_MOCK_LLM=false` to call Groq (`openai/gpt-oss-20b` by default).

---

## Phase 4 — UI & hardening

**Goal:** Demo-ready app with a clear UI, reliable edge handling, and docs.

### Tasks

- [x] Streamlit (or chosen) UI: prefs form → loading state → recommendation cards
- [x] Show name, cuisine, rating, cost, AI explanation (+ optional summary / candidate count)
- [x] Friendly errors: no matches, missing API key, dataset load failure
- [x] Tests for filters, parser, orchestrator; basic logging (candidates, latency, parse ok/fail)
- [x] Polish README; update `pstatement.md` status; run demo checklist

### Exit criteria

- [x] User can submit prefs and understand why each restaurant was suggested
- [x] Demo works without manual code changes; README is enough for someone else to run it

Run: `streamlit run src/app.py` · `pytest tests/`

---

## Definition of done (v1)

- [x] Prefs: location, budget, cuisine, min rating, extra prefs
- [x] Real HF dataset filtered → LLM ranks capped candidates with explanations
- [x] UI shows name, cuisine, rating, cost, explanation
- [x] Grounded results only; empty/failure paths handled cleanly

---

## Optional later (post-v1)

FastAPI `/recommend`, response cache, locality autocomplete, embeddings pre-filter, streaming explanations.

---

## Related docs

- [`pstatement.md`](./pstatement.md) · [`architecture.md`](./architecture.md)
