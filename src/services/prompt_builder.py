"""Build grounded ranking prompts for the LLM."""

from __future__ import annotations

import json
from typing import Sequence

from src.models.preferences import PreferenceInput, Restaurant

SYSTEM_PROMPT = """You are a restaurant recommendation assistant.
Rank restaurants ONLY from the provided candidate list.
Use each restaurant's restaurant_id exactly as given.
Do NOT invent restaurants, ratings, costs, or cuisines.
Do NOT copy or invent facts that are not in the candidate data.
Return ONLY valid JSON (no markdown, no commentary) with this schema:
{
  "summary": "short overview of the shortlist",
  "recommendations": [
    {
      "restaurant_id": "string",
      "rank": 1,
      "explanation": "1-2 sentences on why it fits the user preferences"
    }
  ]
}
Ranks must start at 1 with no gaps. Return at most top_k items.
"""

STRICT_RETRY_SUFFIX = """
Your previous answer was invalid. Reply with ONLY a single JSON object matching the schema.
No markdown fences. No extra keys. Every restaurant_id MUST be from the candidate list.
"""


def _candidate_payload(candidates: Sequence[Restaurant]) -> list[dict]:
    rows = []
    for r in candidates:
        rows.append(
            {
                "restaurant_id": r.restaurant_id,
                "name": r.name,
                "location": r.location,
                "cuisines": r.cuisines,
                "rating": r.rating,
                "cost": r.cost,
                "budget_band": r.budget_band,
                "rest_type": r.rest_type,
                "dish_liked": (r.dish_liked or "")[:120],
            }
        )
    return rows


def build_prompts(
    prefs: PreferenceInput,
    candidates: Sequence[Restaurant],
    *,
    top_k: int,
    strict_retry: bool = False,
) -> tuple[str, str]:
    """Return (system_prompt, user_prompt)."""
    system = SYSTEM_PROMPT
    if strict_retry:
        system = SYSTEM_PROMPT + STRICT_RETRY_SUFFIX

    user_payload = {
        "preferences": {
            "location": prefs.location,
            "budget": prefs.budget,
            "cuisine": prefs.cuisine,
            "min_rating": prefs.min_rating,
            "additional_preferences": prefs.additional_preferences,
        },
        "top_k": top_k,
        "candidates": _candidate_payload(candidates),
    }
    user = (
        "Rank and explain the best restaurants for these preferences.\n"
        + json.dumps(user_payload, ensure_ascii=True)
    )
    return system, user
