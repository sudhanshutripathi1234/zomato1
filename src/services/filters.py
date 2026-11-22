"""Hard filters, soft scoring, and candidate capping."""

from __future__ import annotations

import logging
import re
from typing import Iterable

import pandas as pd

from src.config import Settings, settings
from src.models.preferences import FilterMeta, PreferenceInput, Restaurant

logger = logging.getLogger(__name__)

# Soft-preference keyword → signals checked against rest_type / dish_liked / listed_in_type / etc.
SOFT_PREF_RULES: dict[str, tuple[str, ...]] = {
    "family": ("family", "casual dining", "buffet", "kid", "kids"),
    "family-friendly": ("family", "casual dining", "buffet", "kid", "kids"),
    "family friendly": ("family", "casual dining", "buffet", "kid", "kids"),
    "quick": ("quick bites", "fast food", "delivery"),
    "quick service": ("quick bites", "fast food", "delivery"),
    "fast": ("quick bites", "fast food"),
    "romantic": ("fine dining", "dessert", "bar", "pub"),
    "date": ("fine dining", "dessert", "bar"),
    "outdoor": ("outdoor", "rooftop"),
    "rooftop": ("rooftop",),
    "buffet": ("buffet",),
    "cafe": ("cafe",),
    "delivery": ("delivery", "yes"),
    "online": ("yes",),
    "table booking": ("yes",),
    "book table": ("yes",),
}


def budget_to_cost_bounds(
    budget: str,
    *,
    low_cut: float,
    high_cut: float,
) -> tuple[float | None, float | None]:
    """
    Map budget band to inclusive cost bounds.

    low:    cost <= low_cut
    medium: low_cut < cost <= high_cut
    high:   cost > high_cut
    """
    if budget == "low":
        return (None, low_cut)
    if budget == "medium":
        return (low_cut, high_cut)
    if budget == "high":
        return (high_cut, None)
    raise ValueError(f"Unknown budget band: {budget}")


def infer_budget_cuts_from_frame(df: pd.DataFrame) -> tuple[float, float]:
    """
    Infer low/high cost cuts from precomputed budget_band labels when possible,
    else fall back to cost percentiles.
    """
    if "budget_band" in df.columns and "cost" in df.columns:
        low_costs = df.loc[df["budget_band"] == "low", "cost"].dropna()
        medium_costs = df.loc[df["budget_band"] == "medium", "cost"].dropna()
        if not low_costs.empty and not medium_costs.empty:
            return float(low_costs.max()), float(medium_costs.max())

    valid = df["cost"].dropna() if "cost" in df.columns else pd.Series(dtype=float)
    if valid.empty:
        return 300.0, 550.0
    return float(valid.quantile(0.33)), float(valid.quantile(0.66))


def _location_mask(df: pd.DataFrame, location: str) -> pd.Series:
    needle = location.strip().lower()
    location_col = df["location"].fillna("").astype(str).str.lower()
    city_col = df["city"].fillna("").astype(str).str.lower() if "city" in df.columns else ""
    address_col = (
        df["address"].fillna("").astype(str).str.lower() if "address" in df.columns else ""
    )
    return (
        location_col.str.contains(re.escape(needle), regex=True)
        | (city_col.str.contains(re.escape(needle), regex=True) if isinstance(city_col, pd.Series) else False)
        | (
            address_col.str.contains(re.escape(needle), regex=True)
            if isinstance(address_col, pd.Series)
            else False
        )
    )


def _cuisine_mask(df: pd.DataFrame, cuisine: str) -> pd.Series:
    needle = cuisine.strip().lower()
    tokens = [t for t in re.split(r"[,/|]", needle) if t.strip()]
    if not tokens:
        tokens = [needle]

    cuisine_text = df["cuisines"].fillna("").astype(str).str.lower()

    mask = pd.Series(False, index=df.index)
    for token in tokens:
        token = token.strip()
        if not token:
            continue
        mask = mask | cuisine_text.str.contains(re.escape(token), regex=True)
    return mask


def _rating_mask(df: pd.DataFrame, min_rating: float) -> pd.Series:
    ratings = pd.to_numeric(df["rating"], errors="coerce")
    return ratings >= min_rating


def _budget_mask(df: pd.DataFrame, budget: str) -> pd.Series:
    """Prefer exact budget_band match; fall back to cost bounds if band missing."""
    if "budget_band" in df.columns:
        band_match = df["budget_band"].astype(str).str.lower() == budget
        # Rows with null band are excluded from budget filter
        known = df["budget_band"].notna() & df["budget_band"].astype(str).ne("None")
        return known & band_match

    low_cut, high_cut = infer_budget_cuts_from_frame(df)
    lo, hi = budget_to_cost_bounds(budget, low_cut=low_cut, high_cut=high_cut)
    costs = pd.to_numeric(df["cost"], errors="coerce")
    mask = costs.notna()
    if lo is not None:
        # medium/high lower bound: exclusive of previous band max
        if budget == "medium":
            mask = mask & (costs > lo)
        elif budget == "high":
            mask = mask & (costs > lo)
        else:
            mask = mask & (costs >= lo)
    if hi is not None:
        mask = mask & (costs <= hi)
    return mask


def apply_hard_filters(df: pd.DataFrame, prefs: PreferenceInput) -> tuple[pd.DataFrame, list[str]]:
    """Apply deterministic hard filters; return filtered frame + applied filter names."""
    applied: list[str] = []
    out = df

    mask = _location_mask(out, prefs.location)
    out = out.loc[mask]
    applied.append("location")

    mask = _cuisine_mask(out, prefs.cuisine)
    out = out.loc[mask]
    applied.append("cuisine")

    mask = _rating_mask(out, prefs.min_rating)
    out = out.loc[mask]
    applied.append("rating")

    mask = _budget_mask(out, prefs.budget)
    out = out.loc[mask]
    applied.append("budget")

    return out.copy(), applied


def _parse_soft_tokens(additional_preferences: str) -> list[str]:
    if not additional_preferences or not additional_preferences.strip():
        return []
    text = additional_preferences.strip().lower()
    # Keep multi-word phrases that we know, then fall back to comma/semicolon splits.
    known = sorted(SOFT_PREF_RULES.keys(), key=len, reverse=True)
    found: list[str] = []
    remaining = text
    for phrase in known:
        if phrase in remaining:
            found.append(phrase)
            remaining = remaining.replace(phrase, " ")
    for part in re.split(r"[,;/|]+", remaining):
        token = part.strip()
        if token and token not in found:
            found.append(token)
    return found


def _row_blob(row: pd.Series) -> str:
    parts = [
        str(row.get("rest_type", "") or ""),
        str(row.get("dish_liked", "") or ""),
        str(row.get("listed_in_type", "") or ""),
        str(row.get("cuisines", "") or ""),
        str(row.get("online_order", "") or ""),
        str(row.get("book_table", "") or ""),
    ]
    return " ".join(parts).lower()


def soft_score_rows(df: pd.DataFrame, additional_preferences: str) -> pd.Series:
    """Heuristic soft score from additional preference keywords."""
    tokens = _parse_soft_tokens(additional_preferences)
    if df.empty or not tokens:
        return pd.Series(0.0, index=df.index)

    scores = []
    for _, row in df.iterrows():
        blob = _row_blob(row)
        score = 0.0
        for token in tokens:
            signals = SOFT_PREF_RULES.get(token)
            if signals:
                for signal in signals:
                    if signal == "yes" and token in {"delivery", "online"}:
                        if str(row.get("online_order", "")).strip().lower() == "yes":
                            score += 1.0
                            break
                    elif signal == "yes" and token in {"table booking", "book table"}:
                        if str(row.get("book_table", "")).strip().lower() == "yes":
                            score += 1.0
                            break
                    elif signal in blob:
                        score += 1.0
                        break
            elif token and token in blob:
                score += 0.5
        scores.append(score)
    return pd.Series(scores, index=df.index, dtype=float)


def rank_and_cap(
    df: pd.DataFrame,
    soft_scores: pd.Series,
    *,
    max_candidates: int,
) -> pd.DataFrame:
    """Sort by soft score desc, rating desc, restaurant_id asc; cap size."""
    if df.empty:
        return df.copy()

    ranked = df.copy()
    ranked["soft_score"] = soft_scores.reindex(ranked.index).fillna(0.0)
    ranked["_rating_sort"] = pd.to_numeric(ranked["rating"], errors="coerce").fillna(-1.0)
    ranked["_id_sort"] = ranked["restaurant_id"].astype(str)
    ranked = ranked.sort_values(
        by=["soft_score", "_rating_sort", "_id_sort"],
        ascending=[False, False, True],
        kind="mergesort",
    )
    ranked = ranked.drop(columns=["_rating_sort", "_id_sort"])
    if max_candidates > 0:
        ranked = ranked.head(max_candidates)
    return ranked.reset_index(drop=True)


def filter_candidates(
    df: pd.DataFrame,
    prefs: PreferenceInput,
    *,
    max_candidates: int | None = None,
    cfg: Settings | None = None,
) -> tuple[list[Restaurant], FilterMeta]:
    """
    Full Phase 2 pipeline: hard filters → soft score → sort → cap.

    Returns restaurants and meta (filters_applied, candidate_count, message).
    """
    cfg = cfg or settings
    cap = max_candidates if max_candidates is not None else cfg.max_candidates

    hard, applied = apply_hard_filters(df, prefs)
    hard_count = len(hard)

    if hard.empty:
        meta = FilterMeta(
            filters_applied=applied,
            candidate_count=0,
            hard_match_count=0,
            message="No restaurants matched your filters. Try relaxing location, cuisine, rating, or budget.",
        )
        return [], meta

    scores = soft_score_rows(hard, prefs.additional_preferences)
    capped = rank_and_cap(hard, scores, max_candidates=cap)
    restaurants = [Restaurant.from_row(row) for row in capped.to_dict(orient="records")]

    meta = FilterMeta(
        filters_applied=applied,
        candidate_count=len(restaurants),
        hard_match_count=hard_count,
        message=None,
    )
    logger.info(
        "filter_candidates: hard=%s capped=%s filters=%s",
        hard_count,
        len(restaurants),
        applied,
    )
    return restaurants, meta


def restaurants_from_ids(
    restaurants: Iterable[Restaurant],
    restaurant_ids: Iterable[str],
) -> list[Restaurant]:
    """Helper for later phases: preserve order of ids."""
    by_id = {r.restaurant_id: r for r in restaurants}
    return [by_id[i] for i in restaurant_ids if i in by_id]
