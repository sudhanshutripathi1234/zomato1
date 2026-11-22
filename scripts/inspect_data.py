"""Phase 1 exit check: load the restaurant store and print summary stats."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import settings
from src.data.loader import describe_restaurants
from src.data.store import get_store


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print("Config:")
    print(f"  HF dataset : {settings.hf_dataset_id} [{settings.hf_dataset_split}]")
    print(f"  Cache path : {settings.data_cache_path}")
    print(f"  Top-K      : {settings.top_k}")
    print(f"  Max cands  : {settings.max_candidates}")
    print()

    store = get_store()
    stats = describe_restaurants(store.frame)
    sample = store.get_by_id("0")

    print("Store summary:")
    print(json.dumps(stats, indent=2, default=str))
    print()
    print("Sample get_by_id('0'):")
    if sample is None:
        print("  (missing)")
    else:
        preview = {
            k: sample[k]
            for k in (
                "restaurant_id",
                "name",
                "location",
                "city",
                "cuisines",
                "rating",
                "cost",
                "budget_band",
                "rest_type",
            )
            if k in sample
        }
        print(json.dumps(preview, indent=2, default=str))


if __name__ == "__main__":
    main()
