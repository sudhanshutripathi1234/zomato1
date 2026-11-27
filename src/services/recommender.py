"""End-to-end recommendation orchestration: filter → LLM → grounded DTO."""

from __future__ import annotations

import logging
import time
from typing import Optional

import pandas as pd

from src.config import Settings, settings
from src.llm.client import LLMClient, MockLLMClient, get_llm_client
from src.llm.parser import LLMParseError, ParsedLLMResponse, parse_llm_recommendations
from src.models.preferences import (
    FilterMeta,
    PreferenceInput,
    RecommendationItem,
    RecommendationResponse,
    Restaurant,
)
from src.services.filters import filter_candidates
from src.services.prompt_builder import build_prompts

logger = logging.getLogger(__name__)

FALLBACK_EXPLANATION = "Matches your filters (ranked by rating; LLM ranking unavailable)."


def _to_items_from_parsed(
    parsed: ParsedLLMResponse,
    by_id: dict[str, Restaurant],
) -> list[RecommendationItem]:
    items: list[RecommendationItem] = []
    for row in parsed.recommendations:
        restaurant = by_id.get(row.restaurant_id)
        if restaurant is None:
            continue
        items.append(
            RecommendationItem(
                rank=row.rank,
                restaurant_id=restaurant.restaurant_id,
                name=restaurant.name,
                cuisine=restaurant.cuisines,
                rating=restaurant.rating,
                estimated_cost=restaurant.cost,
                location=restaurant.location,
                address=restaurant.address,
                explanation=row.explanation or FALLBACK_EXPLANATION,
            )
        )
    return items


def _rating_fallback_items(
    candidates: list[Restaurant],
    *,
    top_k: int,
) -> list[RecommendationItem]:
    ranked = sorted(
        candidates,
        key=lambda r: (r.rating is not None, r.rating or -1.0, r.restaurant_id),
        reverse=True,
    )[:top_k]
    return [
        RecommendationItem(
            rank=i,
            restaurant_id=r.restaurant_id,
            name=r.name,
            cuisine=r.cuisines,
            rating=r.rating,
            estimated_cost=r.cost,
            location=r.location,
            address=r.address,
            explanation=FALLBACK_EXPLANATION,
        )
        for i, r in enumerate(ranked, start=1)
    ]


def recommend(
    prefs: PreferenceInput,
    df: pd.DataFrame,
    *,
    llm: Optional[LLMClient] = None,
    cfg: Optional[Settings] = None,
) -> RecommendationResponse:
    """
    Full recommend pipeline.

    1. Filter + soft-score + cap
    2. If empty → empty response (skip LLM)
    3. Prompt LLM → parse grounded JSON
    4. On parse failure: one strict retry, then rating-sorted fallback
    """
    cfg = cfg or settings
    top_k = prefs.top_k or cfg.top_k
    started = time.perf_counter()

    candidates, filter_meta = filter_candidates(df, prefs, cfg=cfg)
    logger.info(
        "recommend: candidates=%s hard_matches=%s top_k=%s location=%s cuisine=%s budget=%s",
        filter_meta.candidate_count,
        filter_meta.hard_match_count,
        top_k,
        prefs.location,
        prefs.cuisine,
        prefs.budget,
    )
    if not candidates:
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.info("recommend: empty candidates; skipping LLM (%.1f ms)", elapsed_ms)
        return RecommendationResponse(
            summary="",
            recommendations=[],
            meta=FilterMeta(
                filters_applied=filter_meta.filters_applied,
                candidate_count=0,
                hard_match_count=filter_meta.hard_match_count,
                message=filter_meta.message,
                used_llm=False,
                used_fallback=False,
                llm_provider=None,
            ),
        )

    client = llm or get_llm_client(cfg)
    provider_name = type(client).__name__

    if isinstance(client, MockLLMClient):
        client.set_candidates(candidates)

    allowed_ids = {r.restaurant_id for r in candidates}
    by_id = {r.restaurant_id: r for r in candidates}

    def _call_and_parse(*, strict_retry: bool) -> ParsedLLMResponse:
        system_prompt, user_prompt = build_prompts(
            prefs, candidates, top_k=top_k, strict_retry=strict_retry
        )
        llm_started = time.perf_counter()
        raw = client.complete(system_prompt, user_prompt)
        llm_ms = (time.perf_counter() - llm_started) * 1000
        parsed = parse_llm_recommendations(raw, allowed_ids=allowed_ids, top_k=top_k)
        logger.info(
            "recommend: parse_ok=true strict_retry=%s llm_latency_ms=%.1f grounded=%s",
            strict_retry,
            llm_ms,
            len(parsed.recommendations),
        )
        return parsed

    try:
        parsed = _call_and_parse(strict_retry=False)
        items = _to_items_from_parsed(parsed, by_id)
        if not items:
            raise LLMParseError("Parsed response produced no joinable items")
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.info(
            "recommend: success used_llm=true recommendations=%s total_ms=%.1f",
            len(items),
            elapsed_ms,
        )
        return RecommendationResponse(
            summary=parsed.summary,
            recommendations=items,
            meta=FilterMeta(
                filters_applied=filter_meta.filters_applied,
                candidate_count=filter_meta.candidate_count,
                hard_match_count=filter_meta.hard_match_count,
                message=None,
                used_llm=True,
                used_fallback=False,
                llm_provider=provider_name,
            ),
        )
    except (LLMParseError, RuntimeError, ValueError, OSError) as first_err:
        logger.warning("recommend: parse_ok=false first_attempt: %s", first_err)

    try:
        parsed = _call_and_parse(strict_retry=True)
        items = _to_items_from_parsed(parsed, by_id)
        if not items:
            raise LLMParseError("Retry produced no joinable items")
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.info(
            "recommend: success after retry used_llm=true recommendations=%s total_ms=%.1f",
            len(items),
            elapsed_ms,
        )
        return RecommendationResponse(
            summary=parsed.summary,
            recommendations=items,
            meta=FilterMeta(
                filters_applied=filter_meta.filters_applied,
                candidate_count=filter_meta.candidate_count,
                hard_match_count=filter_meta.hard_match_count,
                message="Recovered after strict LLM retry.",
                used_llm=True,
                used_fallback=False,
                llm_provider=provider_name,
            ),
        )
    except (LLMParseError, RuntimeError, ValueError, OSError) as retry_err:
        logger.warning("recommend: parse_ok=false retry; using rating fallback: %s", retry_err)

    items = _rating_fallback_items(candidates, top_k=top_k)
    elapsed_ms = (time.perf_counter() - started) * 1000
    logger.info(
        "recommend: fallback used_llm=false recommendations=%s total_ms=%.1f",
        len(items),
        elapsed_ms,
    )
    return RecommendationResponse(
        summary="Showing rating-based matches because LLM ranking was unavailable.",
        recommendations=items,
        meta=FilterMeta(
            filters_applied=filter_meta.filters_applied,
            candidate_count=filter_meta.candidate_count,
            hard_match_count=filter_meta.hard_match_count,
            message="LLM ranking failed; returned rating-sorted fallback.",
            used_llm=False,
            used_fallback=True,
            llm_provider=provider_name,
        ),
    )


class RecommendRestaurants:
    """Thin callable wrapper around recommend() for DI-style usage."""

    def __init__(
        self,
        df: pd.DataFrame,
        *,
        llm: Optional[LLMClient] = None,
        cfg: Optional[Settings] = None,
    ):
        self._df = df
        self._llm = llm
        self._cfg = cfg

    def __call__(self, prefs: PreferenceInput) -> RecommendationResponse:
        return recommend(prefs, self._df, llm=self._llm, cfg=self._cfg)
