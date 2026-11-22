"""LLM client interface with Groq and mock implementations."""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Sequence

from src.config import Settings, settings
from src.models.preferences import Restaurant

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """Vendor-agnostic chat completion client."""

    @abstractmethod
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Return the assistant message content as a string."""


class MockLLMClient(LLMClient):
    """
    Offline client: ranks by rating and returns grounded JSON explanations.

    Used for tests and local runs without a Groq API key.
    """

    def __init__(self, candidates: Sequence[Restaurant] | None = None):
        self._candidates = list(candidates or [])

    def set_candidates(self, candidates: Sequence[Restaurant]) -> None:
        self._candidates = list(candidates)

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        # Prefer candidates injected by the orchestrator; otherwise parse ids from prompt.
        ranked = sorted(
            self._candidates,
            key=lambda r: (r.rating is not None, r.rating or -1.0, r.restaurant_id),
            reverse=True,
        )
        if not ranked:
            ranked_ids = []
        else:
            ranked_ids = [r.restaurant_id for r in ranked]

        recommendations = []
        for i, restaurant in enumerate(ranked, start=1):
            recommendations.append(
                {
                    "restaurant_id": restaurant.restaurant_id,
                    "rank": i,
                    "explanation": (
                        f"Matches your filters with rating "
                        f"{restaurant.rating if restaurant.rating is not None else 'N/A'} "
                        f"and cost {restaurant.cost if restaurant.cost is not None else 'N/A'}."
                    ),
                }
            )

        payload = {
            "summary": "Ranked by rating (mock LLM).",
            "recommendations": recommendations,
        }
        # Touch prompts so unused-arg linters stay quiet and contract stays realistic.
        _ = (system_prompt, user_prompt, ranked_ids)
        return json.dumps(payload)


class GroqLLMClient(LLMClient):
    """Groq chat completions via the official groq SDK."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        temperature: float = 0.2,
        base_url: str | None = None,
    ):
        if not api_key:
            raise ValueError(
                "Groq API key is missing. Set GROQ_API_KEY (or LLM_API_KEY) in .env"
            )
        try:
            from groq import Groq
        except ImportError as exc:
            raise ImportError(
                "The 'groq' package is required. Install with: pip install groq"
            ) from exc

        # groq SDK already defaults to https://api.groq.com/openai/v1.
        # Passing that same path again produces /openai/v1/openai/v1/...
        kwargs = {"api_key": api_key}
        default_base = "https://api.groq.com/openai/v1"
        if base_url and base_url.rstrip("/") not in {
            default_base,
            "https://api.groq.com",
        }:
            kwargs["base_url"] = base_url
        self._client = Groq(**kwargs)
        self._model = model
        self._temperature = temperature

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        logger.info("Calling Groq model=%s", self._model)
        response = self._client.chat.completions.create(
            model=self._model,
            temperature=self._temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("Groq returned an empty response")
        return content


def get_llm_client(cfg: Settings | None = None) -> LLMClient:
    """Factory: mock when USE_MOCK_LLM / provider=mock, else Groq."""
    cfg = cfg or settings
    if cfg.use_mock_llm or cfg.llm_provider == "mock":
        logger.info("Using MockLLMClient")
        return MockLLMClient()
    if cfg.llm_provider in {"groq", ""}:
        return GroqLLMClient(
            api_key=cfg.llm_api_key,
            model=cfg.llm_model,
            temperature=cfg.llm_temperature,
            base_url=cfg.llm_base_url or None,
        )
    raise ValueError(f"Unsupported LLM_PROVIDER: {cfg.llm_provider}")
