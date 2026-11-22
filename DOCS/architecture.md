# Architecture — AI-Powered Restaurant Recommendation System

## 1. Purpose

This document defines the detailed architecture for the Zomato-inspired restaurant recommendation service. The system combines:

1. **Structured filtering** on a real restaurant dataset
2. **LLM reasoning** to rank candidates and explain why each fits the user

Recommendations must be grounded in dataset rows — the LLM ranks and explains; it does not invent restaurants.

---

## 2. High-level architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         PRESENTATION                             │
│  Web UI (forms for prefs + ranked recommendation cards)         │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP / in-process call
┌────────────────────────────▼────────────────────────────────────┐
│                      APPLICATION LAYER                           │
│  Preference validation · Orchestration · Response shaping        │
└───────┬─────────────────────────────────────┬───────────────────┘
        │                                     │
┌───────▼──────────────┐            ┌─────────▼───────────────────┐
│  CANDIDATE RETRIEVAL │            │   RECOMMENDATION ENGINE     │
│  Filter + rank prep  │───────────▶│   Prompt builder + LLM      │
└───────┬──────────────┘            └─────────┬───────────────────┘
        │                                     │
┌───────▼─────────────────────────────────────▼───────────────────┐
│                         DATA LAYER                               │
│  Dataset loader · Preprocessor · In-memory / cached store        │
│  Source: Hugging Face — ManikaSaini/zomato-restaurant-recommendation │
└─────────────────────────────────────────────────────────────────┘
```

**Design principle:** narrow with deterministic filters first, then use the LLM only on a small candidate set for ranking and explanation. This keeps prompts small, latency lower, and results factual.

---

## 3. Logical layers

| Layer | Responsibility | Does not do |
|---|---|---|
| **Presentation** | Collect preferences; render top recommendations (name, cuisine, rating, cost, explanation) | Business rules, LLM calls |
| **Application** | Validate input; orchestrate filter → LLM → response DTO | Own raw dataset parsing |
| **Candidate retrieval** | Apply location / budget / cuisine / rating / soft filters; cap candidate size | Generate natural-language explanations |
| **Recommendation engine** | Build prompt; call LLM; parse ranked list + explanations + optional summary | Load or mutate the full dataset |
| **Data** | Load Hugging Face dataset; clean/normalize columns; expose queryable records | Talk to the LLM |

---

## 4. End-to-end request flow

```
User submits preferences
        │
        ▼
[1] Validate & normalize prefs
    (location, budget band, cuisine, min_rating, extras)
        │
        ▼
[2] Load / use cached restaurant store
        │
        ▼
[3] Hard filters
    · location match
    · cuisine contains / equals
    · rating ≥ min_rating
    · cost within budget band
        │
        ▼
[4] Soft preference scoring (optional)
    · family-friendly, quick service, etc. via keyword / column heuristics
        │
        ▼
[5] Cap candidates (e.g. top N by rating or soft score, N ≤ 15–30)
        │
        ▼
[6] Build LLM prompt
    · system: recommender role + grounding rules
    · user: prefs + structured candidate JSON/table
        │
        ▼
[7] LLM returns ranked IDs + explanations (+ optional summary)
        │
        ▼
[8] Join LLM output back to restaurant records
        │
        ▼
[9] Return / render Top-K recommendations
```

### Sequence (happy path)

```
UI → App → Validator
UI → App → RestaurantStore.query(filters) → candidates
UI → App → PromptBuilder.build(prefs, candidates)
UI → App → LLMClient.complete(prompt) → ranked_payload
UI → App → ResponseMapper.map(ranked_payload, candidates)
UI ← App ← RecommendationResponse
```

### Empty / edge paths

| Condition | Behavior |
|---|---|
| No candidates after hard filters | Skip LLM; return empty result + “relax filters” message |
| LLM parse failure | Retry once with stricter JSON schema instruction; else fall back to rating-sorted candidates with a generic note |
| Dataset load failure | Fail fast at startup or first request with clear error |
| Missing optional columns | Prefer graceful degrade (skip soft filters) over crash |

---

## 5. Component design

### 5.1 Presentation

**Inputs collected**

| Field | Type | Notes |
|---|---|---|
| `location` | string | e.g. Bangalore / locality if available |
| `budget` | enum | `low` \| `medium` \| `high` (mapped to cost ranges) |
| `cuisine` | string | e.g. Italian, Chinese |
| `min_rating` | float | e.g. 3.5–5.0 |
| `additional_preferences` | string / tags | free text or chips (family-friendly, quick service) |
| `top_k` | int | default 5 |

**Outputs shown per recommendation**

- Restaurant name  
- Cuisine  
- Rating  
- Estimated cost  
- AI-generated explanation  
- Optional: overall summary of the set  

### 5.2 Application / orchestration

Single use-case service, e.g. `RecommendRestaurants`:

1. Validate prefs  
2. Resolve budget → cost bounds  
3. Query candidates  
4. If empty → empty response  
5. Else prompt LLM → map → return  

Keeps UI thin and makes the flow testable without a browser.

### 5.3 Data ingestion & store

**Source:** [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)

**Pipeline**

```
Hugging Face load
    → select / rename columns
    → drop null-critical rows (name, location)
    → normalize cuisine strings (split lists, lowercase)
    → coerce rating / cost to numeric
    → derive `budget_band` if useful
    → assign stable `restaurant_id` (index or hash)
    → cache in memory (or parquet / local CSV for offline)
```

**Canonical restaurant record (logical schema)**

| Field | Description |
|---|---|
| `restaurant_id` | Stable id for LLM grounding and join-back |
| `name` | Display name |
| `location` / `city` / `locality` | Geo filters (use what the dataset provides) |
| `cuisines` | List or delimited string |
| `rating` | Numeric average rating |
| `cost` / `approx_cost` | Numeric cost for two (or dataset equivalent) |
| `budget_band` | Derived: low / medium / high |
| `extra_signals` | Optional text fields used for soft prefs (e.g. reviews snippets, features) if present |

Exact column mapping is finalized after inspecting the HF dataset schema at implementation time.

### 5.4 Candidate retrieval

**Hard filters (must match)**

- Location contains / equals user location (case-insensitive)  
- Cuisine overlap with requested cuisine  
- `rating >= min_rating`  
- `cost` within mapped budget range  

**Budget mapping (example — tune after EDA)**

| Budget | Cost rule (illustrative) |
|---|---|
| low | cost ≤ P33 of dataset (or fixed threshold) |
| medium | P33 < cost ≤ P66 |
| high | cost > P66 |

Prefer percentile-based bands from the loaded data so thresholds stay realistic for the corpus.

**Soft filters / scoring**

- Keyword match on additional preferences against available text fields  
- Boost by rating, then by soft-match score  
- Limit to `max_candidates` before LLM  

### 5.5 Recommendation engine (LLM)

**Responsibilities**

- Rank the provided candidates only  
- Explain fit against user prefs  
- Optionally summarize the shortlist  

**Grounding rules (enforced in system prompt)**

- Only recommend restaurants from the supplied candidate list  
- Refer to restaurants by `restaurant_id` (and name)  
- Do not invent ratings, costs, or cuisines  
- Prefer JSON (or another strict schema) for reliable parsing  

**Prompt shape**

```
[System]
You are a restaurant recommender. Rank ONLY from the candidate list.
Return JSON: { "summary": "...", "recommendations": [
  { "restaurant_id": "...", "rank": 1, "explanation": "..." }
]}

[User]
Preferences: { ... }
Candidates: [ { restaurant_id, name, cuisines, rating, cost, location }, ... ]
Return top_k = K
```

**Post-processing**

1. Parse JSON  
2. Validate every `restaurant_id` ∈ candidate set  
3. Drop unknown ids  
4. Join metadata from store  
5. Shape final DTO for UI  

---

## 6. Data contracts

### Preference input

```json
{
  "location": "Bangalore",
  "budget": "medium",
  "cuisine": "Italian",
  "min_rating": 4.0,
  "additional_preferences": "family-friendly",
  "top_k": 5
}
```

### Recommendation response

```json
{
  "summary": "Short AI overview of the shortlist",
  "recommendations": [
    {
      "rank": 1,
      "restaurant_id": "42",
      "name": "Example Trattoria",
      "cuisine": "Italian",
      "rating": 4.5,
      "estimated_cost": 1200,
      "location": "Bangalore",
      "explanation": "Matches Italian + medium budget and strong rating..."
    }
  ],
  "meta": {
    "candidate_count": 18,
    "filters_applied": ["location", "cuisine", "rating", "budget"]
  }
}
```

---

## 7. Suggested technology stack

Not locked by the problem statement; recommended defaults for this repo:

| Concern | Choice | Rationale |
|---|---|---|
| Language | Python 3.11+ | Strong HF / data / LLM ecosystem |
| Dataset | `datasets` (Hugging Face) | Direct load of the specified corpus |
| Data handling | pandas | Filtering and normalization |
| API (optional) | FastAPI | Clean `/recommend` contract if UI is separate |
| UI | Streamlit or simple web frontend | Fast preference form + results |
| LLM | OpenAI-compatible API or local model via adapter | Swappable behind `LLMClient` |
| Config | `.env` + settings module | API keys, model name, candidate caps |
| Caching | In-memory store after first load | Avoid re-downloading dataset every request |

**Key abstraction:** `LLMClient` interface so the rest of the system does not depend on a specific vendor.

---

## 8. Proposed repository structure

```
FOOD/
├── DOCS/
│   ├── pstatement.md
│   ├── pstatement.txt
│   └── architecture.md          ← this file
├── data/                        ← optional local cache / exports
├── src/
│   ├── app.py                   ← UI or API entry
│   ├── config.py
│   ├── models/                  ← prefs, restaurant, response schemas
│   ├── data/
│   │   ├── loader.py            ← HF load + preprocess
│   │   └── store.py             ← query / filter API
│   ├── services/
│   │   ├── recommender.py       ← orchestration
│   │   ├── filters.py           ← hard/soft filtering
│   │   └── prompt_builder.py
│   └── llm/
│       ├── client.py            ← LLMClient interface + impl
│       └── parser.py            ← JSON extract / validate
├── tests/
├── requirements.txt
└── .env.example
```

---

## 9. Cross-cutting concerns

### Configuration

- LLM API key, model name, temperature (low for ranking consistency)  
- `max_candidates`, `top_k` defaults  
- Budget percentile thresholds  
- Dataset name / revision / local cache path  

### Security & privacy

- Keep API keys in environment variables only  
- Do not log full prompts if they contain secrets (usually they won’t)  
- Treat user free-text prefs as untrusted input (length limits)  

### Performance

- Load dataset once; reuse process-lifetime cache  
- Cap candidates sent to the LLM  
- Optional short TTL cache keyed by normalized prefs for repeated queries  

### Observability

- Log: filter counts, candidate size, LLM latency, parse success/fail  
- Surface `meta.candidate_count` to UI for transparency  

### Testing strategy

| Level | What |
|---|---|
| Unit | Budget mapping, filters, prompt builder, JSON parser / id validation |
| Integration | Loader → store → filter with a tiny fixture subset |
| Contract | LLM response schema validation; reject hallucinated ids |
| Manual / E2E | UI submit prefs → see grounded Top-K with explanations |

---

## 10. Extensibility hooks

Future upgrades that fit this architecture without redesign:

- Embeddings + vector search for “similar taste” soft matching before LLM  
- Multi-city routing and locality autocomplete  
- User session history / preference memory  
- A/B different prompt templates  
- Streaming LLM explanations in the UI  

---

## 11. Non-goals (v1)

- Real-time Zomato live API booking or menus  
- User accounts / auth  
- The LLM inventing restaurants outside the filtered candidate set  
- Full ML training pipeline (collaborative filtering) for v1  

---

## 12. Architecture decision summary

| Decision | Choice | Why |
|---|---|---|
| Hybrid retrieval + LLM | Filters first, LLM second | Grounded, cheaper, faster |
| Candidate grounding by id | Stable `restaurant_id` in prompt & join | Prevents hallucination of listings |
| Structured LLM output | JSON recommendations | Reliable UI mapping |
| Thin UI / fat service | Orchestrator service | Testable core logic |
| Vendor-agnostic LLM | `LLMClient` adapter | Swap models without rewriting filters |

---

## Related docs

- Problem / product context: [`pstatement.md`](./pstatement.md)  
- Original brief: [`pstatement.txt`](./pstatement.txt)
