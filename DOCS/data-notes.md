# Data notes — Zomato HF dataset

Source: [`ManikaSaini/zomato-restaurant-recommendation`](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)

~51.7k rows (Bangalore-focused Zomato listings).

## Raw → canonical mapping

| Canonical field | Source column | Notes |
|---|---|---|
| `restaurant_id` | (derived) | Stable string id after clean + dedupe |
| `name` | `name` | Required; blank/null rows dropped |
| `location` | `location` | Locality (e.g. Banashankari) |
| `city` | `listed_in(city)` | Listing city bucket |
| `address` | `address` | Full address string |
| `cuisines` | `cuisines` | Lowercased, comma-joined |
| `cuisine_list` | `cuisines` | Token list for filtering |
| `rating` | `rate` | Parsed from `4.1/5`; `NEW`/`-` → null |
| `votes` | `votes` | Integer, coerced |
| `cost` | `approx_cost(for two people)` | Commas stripped; numeric |
| `budget_band` | (derived from `cost`) | `low` / `medium` / `high` via percentiles |
| `rest_type` | `rest_type` | Useful for soft prefs (e.g. Quick Bites) |
| `online_order` | `online_order` | Yes/No |
| `book_table` | `book_table` | Yes/No |
| `dish_liked` | `dish_liked` | Optional soft-signal text |
| `listed_in_type` | `listed_in(type)` | Buffet, Cafes, etc. |
| `url` | `url` | Zomato URL |

## Cleaning rules

- Drop rows missing `name` or `location`
- Dedupe on `name` + `location` + `address` (dataset repeats venues across listing types)
- Budget bands use configurable percentiles (default P33 / P66)

## Cache

Preprocessed frame is written to `data/restaurants.parquet` (gitignored) after the first successful load.
