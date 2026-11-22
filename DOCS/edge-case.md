# Edge Cases & Corner Scenarios

Catalog of edge cases and corner scenarios for the AI-powered restaurant recommendation system. Aligned with [`architecture.md`](./architecture.md) and [`implementation-plan.md`](./implementation-plan.md).

**Default handling principles**

1. Prefer graceful degrade over crash  
2. Never invent restaurants outside the candidate set  
3. Empty / failure paths must return a clear user-facing message  
4. Deterministic filters run before any LLM call  

---

## 1. Data ingestion & store

| ID | Scenario | Expected behavior |
|---|---|---|
| D01 | Hugging Face download fails (network / 401 / rate limit) | Fail fast with clear error; do not start recommend flow silently |
| D02 | Dataset schema differs from expected column names | Map known aliases or fail with “missing required columns” list |
| D03 | Critical fields null (`name`, `location`) | Drop those rows during preprocess; log drop count |
| D04 | Rating non-numeric / missing (`"NEW"`, `"-"`, blank) | Coerce to NaN; exclude from rating filter or treat as non-matching |
| D05 | Cost non-numeric / missing / zero | Coerce safely; rows without cost excluded from budget filter (or treated as unknown — document choice) |
| D06 | Cuisine is list, comma-string, or mixed case | Normalize to comparable tokens (lowercase, split, strip) |
| D07 | Duplicate restaurant names / near-duplicates | Keep separate ids; do not merge unless explicitly designed |
| D08 | Empty dataset after cleaning | Store load fails or recommend always returns empty with “dataset unavailable” |
| D09 | Very large dataset / slow first load | Load once per process; show UI loading state on first request |
| D10 | Local cache file corrupt / missing | Fall back to HF load or surface clear cache error |
| D11 | Optional columns missing (reviews, features) | Skip soft-pref signals; hard filters still work |
| D12 | Budget percentile bands on tiny / skewed cost distribution | Guard against identical P33/P66; fall back to fixed thresholds if needed |
| D13 | `get_by_id` for unknown id | Return `None` / miss; never invent a record |
| D14 | Concurrent first-load race (multi-session UI) | Single-flight / lock so dataset is not loaded twice unsafely |

---

## 2. User preference validation

| ID | Scenario | Expected behavior |
|---|---|---|
| P01 | Missing required field (e.g. empty location) | Validation error before filters/LLM |
| P02 | Invalid budget (`"cheap"`, blank, wrong case) | Reject or normalize known aliases (`LOW` → `low`); else validation error |
| P03 | `min_rating` out of range (`-1`, `6`, `NaN`) | Clamp to allowed range or reject with message |
| P04 | `min_rating` as string (`"4.5"`) | Coerce if safe; else validation error |
| P05 | `top_k` ≤ 0, fractional, or huge (e.g. 10_000) | Reject or clamp to configured max (e.g. 1–10) |
| P06 | Cuisine empty / whitespace only | Validation error or treat as “any cuisine” — pick one and document |
| P07 | Location typos / alternate spelling (`Bangaluru` vs `Bangalore`) | May return empty; message suggests relaxing / checking spelling |
| P08 | Additional prefs extremely long | Truncate to max length; do not pass unbounded text to LLM |
| P09 | Additional prefs with special chars / injection-like text | Treat as plain text; length-limit; no code execution |
| P10 | Conflicting prefs (e.g. cuisine rare in location + high min rating + low budget) | Allow request; likely empty candidates → relax-filters message |
| P11 | Whitespace / casing in location & cuisine | Trim + case-insensitive matching |
| P12 | Multiple cuisines in one field (`"Italian, Chinese"`) | Support overlap-any or reject; document chosen rule |

---

## 3. Hard filters & budget mapping

| ID | Scenario | Expected behavior |
|---|---|---|
| F01 | No rows match after all hard filters | Skip LLM; empty response + “relax filters” guidance |
| F02 | Location matches city but not locality (or vice versa) | Match against available geo fields; document which fields are searched |
| F03 | Cuisine partial match (`"China"` vs `"Chinese"`) | Prefer token/substring rules that avoid false positives where possible |
| F04 | Multi-cuisine restaurant includes requested cuisine among many | Include (overlap match) |
| F05 | Rating exactly equal to `min_rating` | Include (`>=`) |
| F06 | Cost exactly on budget band boundary | Inclusive bounds on one side only; avoid double-counting across bands |
| F07 | All costs identical → collapsed percentile bands | Use fallback fixed thresholds |
| F08 | Filter order removes everything early | Short-circuit OK; meta should still report what was applied |
| F09 | Only 1 candidate survives | Proceed to LLM (or optional short-circuit with single explanation path) |
| F10 | Candidates >> `max_candidates` before soft sort | Soft-score/sort then cap; never send full corpus to LLM |

---

## 4. Soft scoring & capping

| ID | Scenario | Expected behavior |
|---|---|---|
| S01 | No additional preferences provided | Soft score = 0 for all; sort by rating (or documented default) |
| S02 | Soft keywords not present in any row | No boost; still return hard-filtered set |
| S03 | Soft signal column missing | Degrade gracefully; do not crash |
| S04 | All candidates tie on soft score and rating | Stable sort (e.g. by `restaurant_id`) for determinism |
| S05 | `max_candidates` < `top_k` | Cap LLM input to `max_candidates`; return at most `min(top_k, candidates)` |
| S06 | Soft prefs contradict hard filters | Hard filters win; soft only reorders survivors |
| S07 | Very noisy free-text soft prefs | Keyword extract / ignore stopwords; ignore unmatched tokens |

---

## 5. Prompt building & LLM

| ID | Scenario | Expected behavior |
|---|---|---|
| L01 | Empty candidate list | **Do not call LLM**; return empty result |
| L02 | Missing / invalid API key | Clear config error to UI; mock path still works in dev |
| L03 | LLM timeout / network error | Retry policy (if any) then user-facing failure or rating-sorted fallback |
| L04 | LLM rate limit / 429 | Backoff or friendly “try again” message |
| L05 | LLM returns non-JSON / prose | Retry once with stricter instruction; else fallback |
| L06 | JSON wrapped in markdown fences | Parser strips fences and extracts JSON |
| L07 | JSON missing required fields | Treat as parse failure → retry / fallback |
| L08 | Hallucinated `restaurant_id` not in candidates | Drop those items; never display invented rows |
| L09 | LLM invents rating/cost/cuisine | UI must use store metadata, not LLM-copied facts |
| L10 | LLM returns fewer than `top_k` | Return what is valid; optionally backfill from rating sort |
| L11 | LLM returns more than `top_k` | Truncate to `top_k` after validation |
| L12 | Duplicate ids in LLM output | Keep best rank / first occurrence; drop duplicates |
| L13 | Explanations empty or tiny | Keep row if id valid; show fallback text (“Matches your filters”) |
| L14 | Explanation contradicts data (wrong cuisine claim) | Still show store facts; optional future consistency check |
| L15 | Unsafe / toxic content in model output | Basic sanitize/strip; do not render raw HTML |
| L16 | Oversized prompt (too many candidates / long fields) | Enforce `max_candidates` and field truncation in prompt builder |
| L17 | Provider schema / model change | Fail clearly; `LLMClient` isolation limits blast radius |
| L18 | Mock LLM vs real LLM mismatch | Same response contract; tests run primarily against mock |

---

## 6. Orchestration & response mapping

| ID | Scenario | Expected behavior |
|---|---|---|
| O01 | Happy path | Validated prefs → candidates → LLM → joined Top-K DTO |
| O02 | Empty candidates | Empty recommendations + meta + relax message; LLM skipped |
| O03 | Parse fail then retry success | Return retried result; log retry |
| O04 | Parse fail after retry | Rating-sorted fallback candidates + generic note in summary/meta |
| O05 | All LLM ids invalid | Equivalent to parse failure → fallback |
| O06 | Join step: id valid but record missing from store | Drop item; log inconsistency |
| O07 | `top_k` larger than candidate count | Return all candidates (ranked), not padded fakes |
| O08 | Partial success (some ids good, some bad) | Return only grounded items; meta may note dropped count |
| O09 | Exception mid-pipeline | Catch at orchestrator boundary; map to safe error response for UI |

---

## 7. UI / presentation

| ID | Scenario | Expected behavior |
|---|---|---|
| U01 | Submit with empty required fields | Inline validation; no spinner forever |
| U02 | Long-running LLM call | Loading / disabled submit; avoid double-submit |
| U03 | Double-click submit | Debounce or ignore second submit while in flight |
| U04 | Zero recommendations | Empty state with suggestions (broaden location, lower min rating, etc.) |
| U05 | Fallback recommendations (LLM failed) | Label or note that ranking is rating-based fallback |
| U06 | Missing cost/rating on a displayed row | Show “N/A” rather than blank/crash |
| U07 | Very long restaurant names / explanations | Truncate in card with expand/wrap; layout must not break |
| U08 | Dataset still loading on first open | Show load progress / message |
| U09 | Config error (no API key) | Actionable message; do not dump stack trace |
| U10 | Session refresh mid-request | Recover gracefully; allow resubmit |
| U11 | `candidate_count` shown vs displayed `top_k` | Make clear these are different numbers |

---

## 8. Config, security & operations

| ID | Scenario | Expected behavior |
|---|---|---|
| C01 | `.env` missing | Sensible defaults where safe; fail only for required secrets when real LLM used |
| C02 | Secrets committed accidentally | `.gitignore` + `.env.example` only; never log API keys |
| C03 | Extreme config (`max_candidates=1`, `top_k=50`) | Clamp / validate config at startup |
| C04 | Temperature too high (unstable JSON) | Prefer low temperature default for ranking |
| C05 | Logging PII / full prompts in production | Log sizes/latencies/status; avoid unbounded prompt dumps |
| C06 | Disk full when writing local cache | Catch IO error; continue with in-memory or fail clearly |

---

## 9. Cross-cutting corner cases (high priority)

These are the cases most likely to break a demo if ignored:

1. **No candidates after filters** → skip LLM + relax message  
2. **LLM hallucinated restaurants** → id allowlist + store join only  
3. **LLM non-JSON** → retry once → rating fallback  
4. **Dirty rating/cost values in dataset** → coerce + exclude safely  
5. **Missing API key** → clear UI error; mock path for local/dev  
6. **`top_k` > survivors** → return survivors only  
7. **First-load dataset delay** → cache + UI loading state  
8. **Soft-pref columns absent** → hard filters still succeed  

---

## 10. Suggested test matrix (by phase)

| Phase | Must-cover edge IDs |
|---|---|
| 1 — Foundation & data | D01–D08, D11–D13 |
| 2 — Candidate retrieval | P01–P12, F01–F10, S01–S07 |
| 3 — LLM recommendations | L01–L18, O01–O09 |
| 4 — UI & hardening | U01–U11, C01–C06 + demo of §9 |

---

## Related docs

- [`pstatement.md`](./pstatement.md)  
- [`architecture.md`](./architecture.md)  
- [`implementation-plan.md`](./implementation-plan.md)
