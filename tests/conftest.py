"""Pytest path bootstrap and shared fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def sample_restaurants() -> pd.DataFrame:
    """Tiny deterministic restaurant frame for filter tests."""
    return pd.DataFrame(
        [
            {
                "restaurant_id": "1",
                "name": "Pasta Place",
                "location": "Indiranagar",
                "city": "Indiranagar",
                "address": "12 Main Rd, Indiranagar, Bangalore",
                "cuisines": "italian, cafe",
                "cuisine_list": ["italian", "cafe"],
                "rating": 4.5,
                "votes": 100,
                "cost": 800.0,
                "budget_band": "high",
                "rest_type": "Casual Dining",
                "online_order": "Yes",
                "book_table": "Yes",
                "dish_liked": "Pasta, Pizza",
                "listed_in_type": "Dine-out",
                "url": "",
            },
            {
                "restaurant_id": "2",
                "name": "Quick Dosa",
                "location": "BTM",
                "city": "BTM",
                "address": "BTM Layout, Bangalore",
                "cuisines": "south indian",
                "cuisine_list": ["south indian"],
                "rating": 4.0,
                "votes": 50,
                "cost": 200.0,
                "budget_band": "low",
                "rest_type": "Quick Bites",
                "online_order": "Yes",
                "book_table": "No",
                "dish_liked": "Masala Dosa",
                "listed_in_type": "Delivery",
                "url": "",
            },
            {
                "restaurant_id": "3",
                "name": "China Bowl",
                "location": "Indiranagar",
                "city": "Indiranagar",
                "address": "Indiranagar, Bangalore",
                "cuisines": "chinese, thai",
                "cuisine_list": ["chinese", "thai"],
                "rating": 3.8,
                "votes": 40,
                "cost": 450.0,
                "budget_band": "medium",
                "rest_type": "Casual Dining",
                "online_order": "No",
                "book_table": "No",
                "dish_liked": "Noodles",
                "listed_in_type": "Dine-out",
                "url": "",
            },
            {
                "restaurant_id": "4",
                "name": "Budget Italian",
                "location": "Koramangala",
                "city": "Koramangala",
                "address": "Koramangala, Bangalore",
                "cuisines": "italian",
                "cuisine_list": ["italian"],
                "rating": 4.2,
                "votes": 80,
                "cost": 500.0,
                "budget_band": "medium",
                "rest_type": "Cafe",
                "online_order": "Yes",
                "book_table": "No",
                "dish_liked": "Garlic Bread",
                "listed_in_type": "Cafes",
                "url": "",
            },
            {
                "restaurant_id": "5",
                "name": "Low Rated Italian",
                "location": "Indiranagar",
                "city": "Indiranagar",
                "address": "Indiranagar, Bangalore",
                "cuisines": "italian",
                "cuisine_list": ["italian"],
                "rating": 2.5,
                "votes": 10,
                "cost": 700.0,
                "budget_band": "high",
                "rest_type": "Casual Dining",
                "online_order": "No",
                "book_table": "No",
                "dish_liked": "",
                "listed_in_type": "Dine-out",
                "url": "",
            },
        ]
    )
