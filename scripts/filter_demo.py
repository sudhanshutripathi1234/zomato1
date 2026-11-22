"""Phase 2 demo: run candidate retrieval against the real store."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.store import get_store
from src.models.preferences import PreferenceInput
from src.services.filters import filter_candidates


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
    store = get_store()
    restaurants, meta = filter_candidates(store.frame, prefs)

    print("Preferences:", prefs.model_dump())
    print("Meta:", meta.model_dump())
    print(f"Shortlist ({len(restaurants)}):")
    for r in restaurants[:10]:
        print(
            json.dumps(
                {
                    "restaurant_id": r.restaurant_id,
                    "name": r.name,
                    "location": r.location,
                    "cuisines": r.cuisines,
                    "rating": r.rating,
                    "cost": r.cost,
                    "budget_band": r.budget_band,
                    "soft_score": r.soft_score,
                },
                default=str,
            )
        )


if __name__ == "__main__":
    main()
