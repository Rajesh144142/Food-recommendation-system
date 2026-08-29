# tool_adapter.py
# Bridge between AutoGen and our existing search_foods tool.
#
# AutoGen can only call a normal Python function.
# Our real tool needs a database session (db=...).
# This adapter opens the session, calls search_foods, then closes it.
#
# IMPORTANT:
#   AutoGen / LLM still never talks to PostgreSQL directly.

from __future__ import annotations

import json
from typing import List, Optional

from app.ai.tools.food_tools import search_foods
from app.database.session import SessionLocal


def search_foods_tool(
    query: Optional[str] = None,
    food_category: Optional[str] = None,
    max_calories: Optional[float] = None,
    min_calories: Optional[float] = None,
    min_protein: Optional[float] = None,
    max_protein: Optional[float] = None,
    max_fat: Optional[float] = None,
    min_fibre: Optional[float] = None,
    max_sodium: Optional[float] = None,
    max_sugar: Optional[float] = None,
    tags: Optional[List[str]] = None,
    dietary_types: Optional[List[str]] = None,
    excluded_allergens: Optional[List[str]] = None,
    limit: int = 10,
) -> str:
    """
    Search foods through the app layers.

    Flow:
        AutoGen FoodSearcher
            → search_foods_tool (this function)
            → search_foods
            → FoodService
            → FoodRepository
            → database

    Returns a JSON string so the LLM can read the result easily.
    """
    db = SessionLocal()
    try:
        result = search_foods(
            db=db,
            query=query,
            food_category=food_category,
            max_calories=max_calories,
            min_calories=min_calories,
            min_protein=min_protein,
            max_protein=max_protein,
            max_fat=max_fat,
            min_fibre=min_fibre,
            max_sodium=max_sodium,
            max_sugar=max_sugar,
            tags=tags,
            dietary_types=dietary_types,
            excluded_allergens=excluded_allergens,
            limit=limit,
        )
        return json.dumps(result, indent=2)
    finally:
        db.close()
