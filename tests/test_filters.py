"""Unit tests for Phase 2 candidate retrieval."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.models.preferences import PreferenceInput
from src.services.filters import (
    apply_hard_filters,
    budget_to_cost_bounds,
    filter_candidates,
    rank_and_cap,
    soft_score_rows,
)


def test_budget_to_cost_bounds_mapping():
    assert budget_to_cost_bounds("low", low_cut=300, high_cut=550) == (None, 300)
    assert budget_to_cost_bounds("medium", low_cut=300, high_cut=550) == (300, 550)
    assert budget_to_cost_bounds("high", low_cut=300, high_cut=550) == (550, None)


def test_preference_validation_aliases_and_bounds():
    prefs = PreferenceInput(
        location="  Indiranagar ",
        budget="Cheap",
        cuisine=" Italian ",
        min_rating=4.0,
        top_k=3,
    )
    assert prefs.location == "Indiranagar"
    assert prefs.budget == "low"
    assert prefs.cuisine == "Italian"

    with pytest.raises(ValidationError):
        PreferenceInput(location="", budget="low", cuisine="Italian")

    with pytest.raises(ValidationError):
        PreferenceInput(location="BTM", budget="luxury", cuisine="Italian")

    with pytest.raises(ValidationError):
        PreferenceInput(location="BTM", budget="low", cuisine="Italian", min_rating=6)

    with pytest.raises(ValidationError):
        PreferenceInput(location="BTM", budget="low", cuisine="Italian", top_k=0)


def test_hard_filters_match(sample_restaurants):
    prefs = PreferenceInput(
        location="Indiranagar",
        budget="high",
        cuisine="Italian",
        min_rating=4.0,
    )
    filtered, applied = apply_hard_filters(sample_restaurants, prefs)
    assert applied == ["location", "cuisine", "rating", "budget"]
    assert set(filtered["restaurant_id"]) == {"1"}


def test_hard_filters_empty(sample_restaurants):
    prefs = PreferenceInput(
        location="Nowhereville",
        budget="low",
        cuisine="Italian",
        min_rating=4.0,
    )
    filtered, _ = apply_hard_filters(sample_restaurants, prefs)
    assert filtered.empty


def test_cuisine_overlap_and_rating_boundary(sample_restaurants):
    prefs = PreferenceInput(
        location="Indiranagar",
        budget="medium",
        cuisine="Chinese",
        min_rating=3.8,
    )
    filtered, _ = apply_hard_filters(sample_restaurants, prefs)
    assert set(filtered["restaurant_id"]) == {"3"}


def test_location_matches_address_city(sample_restaurants):
    prefs = PreferenceInput(
        location="Bangalore",
        budget="low",
        cuisine="South Indian",
        min_rating=3.5,
    )
    filtered, _ = apply_hard_filters(sample_restaurants, prefs)
    assert set(filtered["restaurant_id"]) == {"2"}


def test_soft_score_boosts_quick_service(sample_restaurants):
    scores = soft_score_rows(sample_restaurants, "quick service")
    # Quick Dosa (id 2) should score highest
    assert scores.loc[sample_restaurants["restaurant_id"] == "2"].iloc[0] > 0
    assert scores.loc[sample_restaurants["restaurant_id"] == "2"].iloc[0] >= scores.max()


def test_soft_score_zero_without_prefs(sample_restaurants):
    scores = soft_score_rows(sample_restaurants, "")
    assert (scores == 0).all()


def test_rank_and_cap_never_exceeds_max(sample_restaurants):
    scores = soft_score_rows(sample_restaurants, "")
    capped = rank_and_cap(sample_restaurants, scores, max_candidates=2)
    assert len(capped) == 2
    # Default sort by rating desc when soft scores tie
    assert list(capped["restaurant_id"]) == ["1", "4"]


def test_filter_candidates_end_to_end(sample_restaurants):
    prefs = PreferenceInput(
        location="Bangalore",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
        additional_preferences="cafe",
        top_k=5,
    )
    restaurants, meta = filter_candidates(sample_restaurants, prefs, max_candidates=25)
    assert meta.candidate_count == 1
    assert meta.hard_match_count == 1
    assert restaurants[0].restaurant_id == "4"
    assert restaurants[0].soft_score >= 0
    assert "location" in meta.filters_applied


def test_filter_candidates_empty_message(sample_restaurants):
    prefs = PreferenceInput(
        location="Mars",
        budget="high",
        cuisine="Italian",
        min_rating=4.5,
    )
    restaurants, meta = filter_candidates(sample_restaurants, prefs, max_candidates=10)
    assert restaurants == []
    assert meta.candidate_count == 0
    assert meta.message is not None


def test_filter_candidates_respects_cap(sample_restaurants):
    prefs = PreferenceInput(
        location="Bangalore",
        budget="high",
        cuisine="Italian",
        min_rating=2.0,
    )
    # Without cuisine+budget+rating alone we could get multiple; use broad filters
    prefs = PreferenceInput(
        location="Bangalore",
        budget="high",
        cuisine="Italian",
        min_rating=2.0,
    )
    restaurants, meta = filter_candidates(sample_restaurants, prefs, max_candidates=1)
    assert len(restaurants) <= 1
    assert meta.candidate_count <= 1
