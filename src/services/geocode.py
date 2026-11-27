"""Free Nominatim geocoding with a small in-memory cache."""

from __future__ import annotations

import json
import logging
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "SPICE-AI-Restaurant-Recommender/1.0 (local-demo)"
CACHE_LIMIT = 256
MIN_INTERVAL_SEC = 1.05


class GeocodeResult(BaseModel):
    lat: float
    lon: float
    display_name: str = ""


_cache: dict[str, GeocodeResult] = {}
_lock = threading.Lock()
_last_request_at = 0.0


def _normalize_query(query: str) -> str:
    return " ".join(query.strip().split()).lower()


def geocode(query: str, *, timeout: float = 8.0) -> Optional[GeocodeResult]:
    """Resolve a place string to coordinates via Nominatim (cached)."""
    key = _normalize_query(query)
    if not key:
        return None

    with _lock:
        cached = _cache.get(key)
        if cached is not None:
            return cached

    global _last_request_at
    with _lock:
        wait = MIN_INTERVAL_SEC - (time.monotonic() - _last_request_at)
        if wait > 0:
            time.sleep(wait)

        params = urllib.parse.urlencode(
            {
                "q": query.strip(),
                "format": "json",
                "limit": "1",
            }
        )
        request = urllib.request.Request(
            f"{NOMINATIM_URL}?{params}",
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = response.read().decode("utf-8")
        except (urllib.error.URLError, TimeoutError) as exc:
            logger.warning("Nominatim request failed for %r: %s", query, exc)
            _last_request_at = time.monotonic()
            return None
        finally:
            _last_request_at = time.monotonic()

    try:
        rows = json.loads(payload)
    except json.JSONDecodeError:
        logger.warning("Nominatim returned invalid JSON for %r", query)
        return None

    if not isinstance(rows, list) or not rows:
        return None

    row = rows[0]
    try:
        result = GeocodeResult(
            lat=float(row["lat"]),
            lon=float(row["lon"]),
            display_name=str(row.get("display_name") or ""),
        )
    except (KeyError, TypeError, ValueError):
        return None

    with _lock:
        if len(_cache) >= CACHE_LIMIT:
            # Drop an arbitrary oldest-ish entry to bound memory.
            _cache.pop(next(iter(_cache)), None)
        _cache[key] = result
    return result
