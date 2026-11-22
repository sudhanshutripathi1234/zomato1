"""Integration tests for Phase 3 recommend() with mock LLM."""

from __future__ import annotations

import json

from src.llm.client import LLMClient, MockLLMClient
from src.models.preferences import PreferenceInput
from src.services.recommender import recommend


class HallucinatingLLM(LLMClient):
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        return json.dumps(
            {
                "summary": "hallucinated",
                "recommendations": [
                    {
                        "restaurant_id": "not-real",
                        "rank": 1,
                        "explanation": "Invented place",
                    }
                ],
            }
        )


class BadThenGoodLLM(LLMClient):
    def __init__(self):
        self.calls = 0

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        self.calls += 1
        if self.calls == 1:
            return "THIS IS NOT JSON"
        return json.dumps(
            {
                "summary": "recovered",
                "recommendations": [
                    {
                        "restaurant_id": "4",
                        "rank": 1,
                        "explanation": "Solid Italian cafe match",
                    }
                ],
            }
        )


def test_recommend_mock_grounded_topk(sample_restaurants):
    prefs = PreferenceInput(
        location="Bangalore",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
        top_k=3,
    )
    response = recommend(prefs, sample_restaurants, llm=MockLLMClient())
    assert response.meta.used_llm is True
    assert response.meta.used_fallback is False
    assert len(response.recommendations) >= 1
    assert all(r.restaurant_id in {"4"} for r in response.recommendations)
    assert response.recommendations[0].explanation
    assert response.recommendations[0].name == "Budget Italian"


def test_recommend_empty_skips_llm(sample_restaurants):
    class ExplodingLLM(LLMClient):
        def complete(self, system_prompt: str, user_prompt: str) -> str:
            raise AssertionError("LLM should not be called for empty candidates")

    prefs = PreferenceInput(
        location="Mars",
        budget="high",
        cuisine="Italian",
        min_rating=4.5,
    )
    response = recommend(prefs, sample_restaurants, llm=ExplodingLLM())
    assert response.recommendations == []
    assert response.meta.used_llm is False
    assert response.meta.message is not None


def test_hallucinated_ids_never_returned(sample_restaurants):
    prefs = PreferenceInput(
        location="Bangalore",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
        top_k=3,
    )
    response = recommend(prefs, sample_restaurants, llm=HallucinatingLLM())
    # First + retry both hallucinate → rating fallback, still grounded
    assert response.meta.used_fallback is True
    assert all(r.restaurant_id == "4" for r in response.recommendations)
    assert "not-real" not in {r.restaurant_id for r in response.recommendations}


def test_retry_recovers_from_bad_json(sample_restaurants):
    prefs = PreferenceInput(
        location="Bangalore",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
        top_k=1,
    )
    llm = BadThenGoodLLM()
    response = recommend(prefs, sample_restaurants, llm=llm)
    assert llm.calls == 2
    assert response.meta.used_llm is True
    assert response.meta.used_fallback is False
    assert response.recommendations[0].restaurant_id == "4"
    assert "Italian cafe" in response.recommendations[0].explanation
