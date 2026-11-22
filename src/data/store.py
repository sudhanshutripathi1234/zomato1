"""In-memory restaurant store with load-once caching."""

from __future__ import annotations

import logging
import threading
from typing import Any

import pandas as pd

from src.config import Settings, settings
from src.data.loader import load_restaurants

logger = logging.getLogger(__name__)


class RestaurantStore:
    """Process-lifetime cache of preprocessed restaurant records."""

    def __init__(self, df: pd.DataFrame):
        self._df = df.copy()
        self._by_id = {
            str(row["restaurant_id"]): row.to_dict()
            for _, row in self._df.iterrows()
        }

    @classmethod
    def from_settings(cls, cfg: Settings | None = None) -> "RestaurantStore":
        cfg = cfg or settings
        df = load_restaurants(cfg)
        return cls(df)

    @property
    def frame(self) -> pd.DataFrame:
        return self._df.copy()

    def __len__(self) -> int:
        return len(self._df)

    def list(self, limit: int | None = None) -> list[dict[str, Any]]:
        frame = self._df if limit is None else self._df.head(limit)
        return frame.to_dict(orient="records")

    def get_by_id(self, restaurant_id: str) -> dict[str, Any] | None:
        return self._by_id.get(str(restaurant_id))

    def sample_locations(self, n: int = 10) -> list[str]:
        values = sorted(self._df["location"].dropna().unique())
        return values[:n]

    def rating_range(self) -> tuple[float | None, float | None]:
        if self._df["rating"].notna().any():
            return float(self._df["rating"].min()), float(self._df["rating"].max())
        return None, None

    def cost_range(self) -> tuple[float | None, float | None]:
        if self._df["cost"].notna().any():
            return float(self._df["cost"].min()), float(self._df["cost"].max())
        return None, None


_store: RestaurantStore | None = None
_store_lock = threading.Lock()


def get_store(cfg: Settings | None = None, *, force_reload: bool = False) -> RestaurantStore:
    """Return a singleton RestaurantStore (load-once per process)."""
    global _store
    if _store is not None and not force_reload:
        return _store

    with _store_lock:
        if _store is not None and not force_reload:
            return _store
        logger.info("Initializing RestaurantStore")
        _store = RestaurantStore.from_settings(cfg)
        logger.info("RestaurantStore ready: %s rows", len(_store))
        return _store
