"""Load and preprocess the Hugging Face Zomato restaurant dataset."""

from __future__ import annotations

import logging
import re
from pathlib import Path

import pandas as pd
from datasets import load_dataset

from src.config import Settings, settings

logger = logging.getLogger(__name__)

CANONICAL_COLUMNS = [
    "restaurant_id",
    "name",
    "location",
    "city",
    "address",
    "cuisines",
    "cuisine_list",
    "rating",
    "votes",
    "cost",
    "budget_band",
    "rest_type",
    "online_order",
    "book_table",
    "dish_liked",
    "listed_in_type",
    "url",
]


def _parse_rating(value: object) -> float | None:
    """Parse values like '4.1/5', 'NEW', '-', None into a float or None."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    if not text or text in {"-", "NEW", "nan", "None"}:
        return None
    match = re.match(r"^(\d+(?:\.\d+)?)", text)
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def _parse_cost(value: object) -> float | None:
    """Parse approx cost strings that may include commas."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip().replace(",", "")
    if not text or text in {"-", "nan", "None"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _normalize_cuisines(value: object) -> list[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    parts = [p.strip().lower() for p in str(value).split(",")]
    return [p for p in parts if p]


def _derive_budget_band(
    costs: pd.Series,
    low_percentile: float,
    high_percentile: float,
) -> tuple[pd.Series, float, float]:
    """Map numeric cost to low/medium/high using dataset percentiles."""
    valid = costs.dropna()
    if valid.empty:
        bands = pd.Series(["medium"] * len(costs), index=costs.index)
        return bands, 0.0, 0.0

    low_cut = float(valid.quantile(low_percentile / 100.0))
    high_cut = float(valid.quantile(high_percentile / 100.0))

    # Guard collapsed percentiles on skewed/tiny distributions.
    if high_cut <= low_cut:
        low_cut = float(valid.quantile(0.33))
        high_cut = float(valid.quantile(0.66))
    if high_cut <= low_cut:
        median = float(valid.median())
        low_cut = median
        high_cut = median

    def _band(cost: float | None) -> str | None:
        if cost is None or pd.isna(cost):
            return None
        if cost <= low_cut:
            return "low"
        if cost <= high_cut:
            return "medium"
        return "high"

    bands = costs.map(_band)
    return bands, low_cut, high_cut


def preprocess_restaurants(
    raw: pd.DataFrame,
    *,
    low_percentile: float = 33.0,
    high_percentile: float = 66.0,
) -> pd.DataFrame:
    """Clean and normalize raw HF rows into the canonical restaurant schema."""
    before = len(raw)
    df = raw.copy()

    required = {"name", "location"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing required columns: {sorted(missing)}")

    df["name"] = df["name"].astype(str).str.strip()
    df["location"] = df["location"].astype(str).str.strip()

    df = df[df["name"].ne("") & df["name"].ne("nan")]
    df = df[df["location"].ne("") & df["location"].ne("nan")]
    df = df.dropna(subset=["name", "location"])

    df["rating"] = df["rate"].map(_parse_rating) if "rate" in df.columns else None
    df["cost"] = (
        df["approx_cost(for two people)"].map(_parse_cost)
        if "approx_cost(for two people)" in df.columns
        else None
    )
    df["cuisine_list"] = (
        df["cuisines"].map(_normalize_cuisines) if "cuisines" in df.columns else [[] for _ in range(len(df))]
    )
    df["cuisines"] = df["cuisine_list"].map(lambda items: ", ".join(items))

    df["city"] = (
        df["listed_in(city)"].astype(str).str.strip()
        if "listed_in(city)" in df.columns
        else ""
    )
    df["listed_in_type"] = (
        df["listed_in(type)"].astype(str).str.strip()
        if "listed_in(type)" in df.columns
        else ""
    )
    df["address"] = df["address"].astype(str).str.strip() if "address" in df.columns else ""
    df["rest_type"] = (
        df["rest_type"].astype(str).str.strip() if "rest_type" in df.columns else ""
    )
    df["online_order"] = (
        df["online_order"].astype(str).str.strip() if "online_order" in df.columns else ""
    )
    df["book_table"] = (
        df["book_table"].astype(str).str.strip() if "book_table" in df.columns else ""
    )
    df["dish_liked"] = (
        df["dish_liked"].astype(str).str.strip() if "dish_liked" in df.columns else ""
    )
    df["url"] = df["url"].astype(str).str.strip() if "url" in df.columns else ""
    df["votes"] = pd.to_numeric(df.get("votes"), errors="coerce").fillna(0).astype(int)

    budget_band, low_cut, high_cut = _derive_budget_band(
        df["cost"], low_percentile, high_percentile
    )
    df["budget_band"] = budget_band

    df = df.reset_index(drop=True)
    df.insert(0, "restaurant_id", df.index.astype(str))

    # Prefer first occurrence of a name+location+address triple to reduce near-dup noise
    # from listed_in(type)/city expansions, while keeping stable ids on the kept rows.
    dedupe_keys = ["name", "location", "address"]
    before_dedupe = len(df)
    df = df.drop_duplicates(subset=dedupe_keys, keep="first").reset_index(drop=True)
    df["restaurant_id"] = df.index.astype(str)

    out = df[[c for c in CANONICAL_COLUMNS if c in df.columns]].copy()
    after = len(out)
    logger.info(
        "Preprocessed restaurants: %s -> %s rows (dropped %s; deduped %s). "
        "Budget cuts: low<=%.0f, medium<=%.0f, else high.",
        before,
        after,
        before - before_dedupe,
        before_dedupe - after,
        low_cut,
        high_cut,
    )
    return out


def load_restaurants(
    cfg: Settings | None = None,
    *,
    use_cache: bool = True,
    save_cache: bool = True,
) -> pd.DataFrame:
    """
    Load restaurants from local parquet cache or Hugging Face, then preprocess.

    Cache stores the *preprocessed* frame for faster subsequent loads.
    """
    cfg = cfg or settings
    cache_path = cfg.data_cache_path

    if use_cache and cache_path.exists():
        logger.info("Loading restaurants from cache: %s", cache_path)
        df = pd.read_parquet(cache_path)
        logger.info("Cached restaurants loaded: %s rows", len(df))
        return df

    logger.info(
        "Loading Hugging Face dataset %s [%s]",
        cfg.hf_dataset_id,
        cfg.hf_dataset_split,
    )
    dataset = load_dataset(cfg.hf_dataset_id, split=cfg.hf_dataset_split)
    raw = dataset.to_pandas()
    df = preprocess_restaurants(
        raw,
        low_percentile=cfg.budget_low_percentile,
        high_percentile=cfg.budget_high_percentile,
    )

    if save_cache:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(cache_path, index=False)
        logger.info("Wrote restaurant cache: %s", cache_path)

    return df


def describe_restaurants(df: pd.DataFrame) -> dict[str, object]:
    """Summary stats used for Phase 1 exit-criteria checks."""
    return {
        "row_count": int(len(df)),
        "unique_locations": int(df["location"].nunique()),
        "sample_locations": sorted(df["location"].dropna().unique())[:10],
        "sample_cuisines": sorted(
            {c for row in df["cuisine_list"] for c in (row or [])}
        )[:15],
        "rating_min": float(df["rating"].min(skipna=True)) if df["rating"].notna().any() else None,
        "rating_max": float(df["rating"].max(skipna=True)) if df["rating"].notna().any() else None,
        "cost_min": float(df["cost"].min(skipna=True)) if df["cost"].notna().any() else None,
        "cost_max": float(df["cost"].max(skipna=True)) if df["cost"].notna().any() else None,
        "budget_band_counts": df["budget_band"].value_counts(dropna=False).to_dict(),
    }
