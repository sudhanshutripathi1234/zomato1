"""FastAPI entrypoint — /health, /meta, /recommend."""

from __future__ import annotations

import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import settings
from src.data.store import RestaurantStore, get_store
from src.models.preferences import PreferenceInput, RecommendationResponse
from src.services.recommender import recommend

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("src.api")

_DEFAULT_CORS_ORIGINS = (
    "http://localhost:3000,"
    "http://127.0.0.1:3000"
)


def _cors_origins() -> list[str]:
    """Comma-separated origins from CORS_ORIGINS (includes Vercel in production)."""
    raw = os.getenv("CORS_ORIGINS", _DEFAULT_CORS_ORIGINS)
    origins = [part.strip() for part in raw.split(",") if part.strip()]
    return origins or [p.strip() for p in _DEFAULT_CORS_ORIGINS.split(",")]


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    try:
        store = get_store(settings)
        logger.info("API store warm: %s restaurants", len(store))
    except Exception:  # noqa: BLE001
        logger.exception("Store warm failed; /meta and /recommend will retry")
    yield


_origins = _cors_origins()
logger.info("CORS allow_origins=%s", _origins)

app = FastAPI(
    title="Restaurant Recommender API",
    version="1.0.0",
    description="Filter Zomato listings, then LLM-rank grounded candidates.",
    lifespan=_lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MetaResponse(BaseModel):
    locations: list[str]
    restaurant_count: int
    mode: str
    model: str
    use_mock_llm: bool
    popular_cuisines: list[str]


POPULAR_CUISINES = [
    "North Indian",
    "Chinese",
    "South Indian",
    "Fast Food",
    "Biryani",
    "Cafe",
    "Italian",
    "Continental",
    "Desserts",
    "Street Food",
]


def _store() -> RestaurantStore:
    try:
        return get_store(settings)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Dataset load failed")
        raise HTTPException(
            status_code=503,
            detail=(
                "Could not load the restaurant dataset. Check your network, "
                "DATA_CACHE_PATH, or regenerate the local parquet cache."
            ),
        ) from exc


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/meta", response_model=MetaResponse)
def meta() -> MetaResponse:
    store = _store()
    locations = sorted(
        store.frame["location"].dropna().astype(str).unique().tolist()
    )
    if settings.use_mock_llm:
        mode = "Mock LLM (offline)"
        model = "mock"
    else:
        mode = "Groq"
        model = settings.llm_model
    return MetaResponse(
        locations=locations,
        restaurant_count=len(store),
        mode=mode,
        model=model,
        use_mock_llm=settings.use_mock_llm,
        popular_cuisines=POPULAR_CUISINES,
    )


@app.post("/recommend", response_model=RecommendationResponse)
def recommend_endpoint(body: PreferenceInput) -> RecommendationResponse:
    if not settings.use_mock_llm and not settings.llm_api_key:
        raise HTTPException(
            status_code=401,
            detail=(
                "Groq API key is missing or invalid. Set GROQ_API_KEY in .env, "
                "or set USE_MOCK_LLM=true for offline demo mode."
            ),
        )

    store = _store()
    try:
        return recommend(body, store.frame)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Recommend failed")
        raise HTTPException(
            status_code=500,
            detail=f"Something went wrong: {exc}",
        ) from exc


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "service": "restaurant-recommender",
        "docs": "/docs",
        "endpoints": ["/health", "/meta", "/recommend"],
    }
