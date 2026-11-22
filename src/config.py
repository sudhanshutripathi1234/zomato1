"""Application settings loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Project root: FOOD/
ROOT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(ROOT_DIR / ".env")

GROQ_DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_DEFAULT_MODEL = "openai/gpt-oss-20b"


def _env_str(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


def _env_float(key: str, default: float) -> float:
    raw = os.getenv(key)
    if raw is None or raw.strip() == "":
        return default
    return float(raw)


def _env_int(key: str, default: int) -> int:
    raw = os.getenv(key)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def _env_bool(key: str, default: bool = False) -> bool:
    raw = os.getenv(key)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Runtime configuration for data loading and recommendations."""

    llm_api_key: str
    llm_model: str
    llm_temperature: float
    llm_base_url: str
    llm_provider: str
    use_mock_llm: bool

    top_k: int
    max_candidates: int

    budget_low_percentile: float
    budget_high_percentile: float

    hf_dataset_id: str
    hf_dataset_split: str
    data_cache_path: Path

    @classmethod
    def from_env(cls) -> "Settings":
        cache = _env_str("DATA_CACHE_PATH", "data/restaurants.parquet")
        cache_path = Path(cache)
        if not cache_path.is_absolute():
            cache_path = ROOT_DIR / cache_path

        # Prefer GROQ_API_KEY; fall back to LLM_API_KEY for compatibility.
        api_key = _env_str("GROQ_API_KEY") or _env_str("LLM_API_KEY")

        return cls(
            llm_api_key=api_key,
            llm_model=_env_str("LLM_MODEL", GROQ_DEFAULT_MODEL),
            llm_temperature=_env_float("LLM_TEMPERATURE", 0.2),
            llm_base_url=_env_str("LLM_BASE_URL", GROQ_DEFAULT_BASE_URL),
            llm_provider=_env_str("LLM_PROVIDER", "groq").lower(),
            use_mock_llm=_env_bool("USE_MOCK_LLM", False),
            top_k=_env_int("TOP_K", 5),
            max_candidates=_env_int("MAX_CANDIDATES", 25),
            budget_low_percentile=_env_float("BUDGET_LOW_PERCENTILE", 33.0),
            budget_high_percentile=_env_float("BUDGET_HIGH_PERCENTILE", 66.0),
            hf_dataset_id=_env_str(
                "HF_DATASET_ID",
                "ManikaSaini/zomato-restaurant-recommendation",
            ),
            hf_dataset_split=_env_str("HF_DATASET_SPLIT", "train"),
            data_cache_path=cache_path,
        )


settings = Settings.from_env()
