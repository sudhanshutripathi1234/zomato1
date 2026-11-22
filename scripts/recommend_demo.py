"""Phase 3 demo: end-to-end recommend() (mock or Groq via .env)."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import settings
from src.data.store import get_store
from src.models.preferences import PreferenceInput
from src.services.recommender import recommend


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    prefs = PreferenceInput(
        location="Indiranagar",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
        additional_preferences="cafe",
        top_k=5,
    )
    print(
        f"Provider={settings.llm_provider} model={settings.llm_model} "
        f"use_mock={settings.use_mock_llm}"
    )
    store = get_store()
    response = recommend(prefs, store.frame)
    print("Meta:", response.meta.model_dump())
    print("Summary:", response.summary)
    for item in response.recommendations:
        print(json.dumps(item.model_dump(), default=str))


if __name__ == "__main__":
    main()
