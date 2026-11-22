"""Unit tests for LLM JSON parsing and grounding."""

from __future__ import annotations

import pytest

from src.llm.parser import LLMParseError, parse_llm_recommendations


def test_parse_plain_json_and_truncate():
    text = """
    {
      "summary": "Great picks",
      "recommendations": [
        {"restaurant_id": "1", "rank": 1, "explanation": "Best fit"},
        {"restaurant_id": "2", "rank": 2, "explanation": "Also good"},
        {"restaurant_id": "3", "rank": 3, "explanation": "Third"}
      ]
    }
    """
    parsed = parse_llm_recommendations(text, allowed_ids={"1", "2", "3"}, top_k=2)
    assert parsed.summary == "Great picks"
    assert [r.restaurant_id for r in parsed.recommendations] == ["1", "2"]


def test_parse_markdown_fenced_json():
    text = """Here you go:
```json
{"summary": "ok", "recommendations": [{"restaurant_id": "9", "rank": 1, "explanation": "fit"}]}
```
"""
    parsed = parse_llm_recommendations(text, allowed_ids={"9"}, top_k=5)
    assert parsed.recommendations[0].restaurant_id == "9"


def test_drop_hallucinated_ids():
    text = """
    {
      "summary": "mixed",
      "recommendations": [
        {"restaurant_id": "ghost", "rank": 1, "explanation": "fake"},
        {"restaurant_id": "1", "rank": 2, "explanation": "real"}
      ]
    }
    """
    parsed = parse_llm_recommendations(text, allowed_ids={"1"}, top_k=5)
    assert [r.restaurant_id for r in parsed.recommendations] == ["1"]
    assert parsed.recommendations[0].rank == 1


def test_all_hallucinated_raises():
    text = """
    {"summary": "bad", "recommendations": [{"restaurant_id": "x", "rank": 1, "explanation": "nope"}]}
    """
    with pytest.raises(LLMParseError):
        parse_llm_recommendations(text, allowed_ids={"1"}, top_k=5)


def test_invalid_json_raises():
    with pytest.raises(LLMParseError):
        parse_llm_recommendations("not json at all", allowed_ids={"1"}, top_k=3)
