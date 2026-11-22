"""Parse and validate grounded LLM recommendation JSON."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


class ParsedRecommendation(BaseModel):
    restaurant_id: str
    rank: int = Field(ge=1)
    explanation: str = ""


class ParsedLLMResponse(BaseModel):
    summary: str = ""
    recommendations: list[ParsedRecommendation] = Field(default_factory=list)


class LLMParseError(ValueError):
    """Raised when the model output cannot be parsed into the expected schema."""


def extract_json_object(text: str) -> dict[str, Any]:
    """Extract a JSON object from raw model text (plain or markdown-fenced)."""
    if not text or not text.strip():
        raise LLMParseError("Empty LLM response")

    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, flags=re.DOTALL)
    if fence:
        cleaned = fence.group(1)
    else:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise LLMParseError("No JSON object found in LLM response")
        cleaned = cleaned[start : end + 1]

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise LLMParseError(f"Invalid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise LLMParseError("LLM JSON root must be an object")
    return data


def parse_llm_recommendations(
    text: str,
    *,
    allowed_ids: set[str],
    top_k: int,
) -> ParsedLLMResponse:
    """
    Parse LLM output and keep only grounded restaurant ids.

    - Drops unknown ids (hallucinations)
    - Dedupes by restaurant_id (keeps best/first rank)
    - Truncates to top_k after sorting by rank
    """
    raw = extract_json_object(text)
    try:
        parsed = ParsedLLMResponse.model_validate(raw)
    except ValidationError as exc:
        raise LLMParseError(f"Schema validation failed: {exc}") from exc

    seen: set[str] = set()
    grounded: list[ParsedRecommendation] = []
    dropped = 0

    # Sort by rank ascending first
    ordered = sorted(parsed.recommendations, key=lambda r: r.rank)
    for item in ordered:
        rid = str(item.restaurant_id)
        if rid not in allowed_ids:
            dropped += 1
            continue
        if rid in seen:
            dropped += 1
            continue
        seen.add(rid)
        grounded.append(
            ParsedRecommendation(
                restaurant_id=rid,
                rank=len(grounded) + 1,
                explanation=(item.explanation or "").strip(),
            )
        )
        if len(grounded) >= top_k:
            break

    if not grounded and parsed.recommendations:
        # All ids were invalid → treat as parse failure for retry/fallback.
        raise LLMParseError("No grounded restaurant ids in LLM recommendations")

    if dropped:
        logger.info("Dropped %s ungrounded/duplicate LLM recommendation rows", dropped)

    return ParsedLLMResponse(summary=parsed.summary or "", recommendations=grounded)
