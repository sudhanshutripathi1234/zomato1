"""User preference and restaurant domain models."""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

BudgetBand = Literal["low", "medium", "high"]

MAX_ADDITIONAL_PREFS_LEN = 300
MIN_RATING = 0.0
MAX_RATING = 5.0
MIN_TOP_K = 1
MAX_TOP_K = 10


class PreferenceInput(BaseModel):
    """Validated user preferences for candidate retrieval."""

    location: str = Field(..., min_length=1)
    budget: BudgetBand
    cuisine: str = Field(..., min_length=1)
    min_rating: float = Field(default=3.5, ge=MIN_RATING, le=MAX_RATING)
    additional_preferences: str = Field(default="", max_length=MAX_ADDITIONAL_PREFS_LEN)
    top_k: int = Field(default=5, ge=MIN_TOP_K, le=MAX_TOP_K)

    @field_validator("location", "cuisine", mode="before")
    @classmethod
    def _strip_required_text(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("budget", mode="before")
    @classmethod
    def _normalize_budget(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip().lower()
            aliases = {
                "low": "low",
                "cheap": "low",
                "budget": "low",
                "medium": "medium",
                "mid": "medium",
                "moderate": "medium",
                "high": "high",
                "expensive": "high",
                "premium": "high",
            }
            return aliases.get(normalized, normalized)
        return value

    @field_validator("additional_preferences", mode="before")
    @classmethod
    def _normalize_additional(cls, value: object) -> object:
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()[:MAX_ADDITIONAL_PREFS_LEN]
        return value

    @model_validator(mode="after")
    def _reject_blank_location_cuisine(self) -> "PreferenceInput":
        if not self.location:
            raise ValueError("location must not be blank")
        if not self.cuisine:
            raise ValueError("cuisine must not be blank")
        return self


class Restaurant(BaseModel):
    """Canonical restaurant record used in shortlists."""

    restaurant_id: str
    name: str
    location: str
    city: str = ""
    address: str = ""
    cuisines: str = ""
    cuisine_list: list[str] = Field(default_factory=list)
    rating: Optional[float] = None
    votes: int = 0
    cost: Optional[float] = None
    budget_band: Optional[str] = None
    rest_type: str = ""
    online_order: str = ""
    book_table: str = ""
    dish_liked: str = ""
    listed_in_type: str = ""
    url: str = ""
    soft_score: float = 0.0

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "Restaurant":
        data = dict(row)
        cuisine_list = data.get("cuisine_list")
        if cuisine_list is None:
            cuisine_list = []
        elif hasattr(cuisine_list, "tolist"):
            cuisine_list = cuisine_list.tolist()
        if isinstance(cuisine_list, str):
            cuisine_list = [c.strip() for c in cuisine_list.split(",") if c.strip()]
        data["cuisine_list"] = list(cuisine_list)
        data["restaurant_id"] = str(data.get("restaurant_id", ""))
        # pandas may use NaN
        for key in ("rating", "cost"):
            value = data.get(key)
            if value is not None and value == value:  # not NaN
                data[key] = float(value)
            else:
                data[key] = None
        band = data.get("budget_band")
        if band is None or (isinstance(band, float) and band != band):
            data["budget_band"] = None
        else:
            data["budget_band"] = str(band)
        return cls.model_validate(data)


class FilterMeta(BaseModel):
    filters_applied: list[str] = Field(default_factory=list)
    candidate_count: int = 0
    hard_match_count: int = 0
    message: Optional[str] = None
    used_llm: bool = False
    used_fallback: bool = False
    llm_provider: Optional[str] = None


class RecommendationItem(BaseModel):
    """Single recommendation row (filled fully in Phase 3)."""

    rank: int
    restaurant_id: str
    name: str
    cuisine: str = ""
    rating: Optional[float] = None
    estimated_cost: Optional[float] = None
    location: str = ""
    address: str = ""
    explanation: str = ""


class RecommendationResponse(BaseModel):
    """API/UI response stub; explanations arrive in Phase 3."""

    summary: str = ""
    recommendations: list[RecommendationItem] = Field(default_factory=list)
    meta: FilterMeta = Field(default_factory=FilterMeta)
