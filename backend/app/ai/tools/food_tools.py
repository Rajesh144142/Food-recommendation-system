# food_tools.py
# This file defines the search_foods TOOL.
#
# Important idea:
#   The LLM will NOT connect to PostgreSQL.
#   The LLM will only see TOOL_DEFINITION (the schema below).
#   When the LLM wants data, it asks to run search_foods(...).
#   Our Python function then calls FoodService → FoodRepository → PostgreSQL.

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.schemas.food import SearchFoodsArguments
from app.services.food_service import FoodService


# ==================================================
# TOOL DEFINITION
# This JSON-like dictionary can later be given to an LLM.
# The LLM reads this to understand:
#   - tool name
#   - what it does
#   - which arguments it accepts
# ==================================================

SEARCH_FOODS_TOOL_DEFINITION = {
    "name": "search_foods",
    "description": (
        "Search the food database using food name, description, category, "
        "nutritional requirements, tags, dietary types, and allergen exclusions."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Food name or description to search for.",
            },
            "food_category": {
                "type": "string",
                "description": "Food category such as main_course, snack, or dessert.",
            },
            "max_calories": {
                "type": "number",
                "description": "Maximum calories allowed.",
            },
            "min_calories": {
                "type": "number",
                "description": "Minimum calories required.",
            },
            "min_protein": {
                "type": "number",
                "description": "Minimum protein in grams.",
            },
            "max_protein": {
                "type": "number",
                "description": "Maximum protein in grams.",
            },
            "max_fat": {
                "type": "number",
                "description": "Maximum fat in grams (useful for lower-fat meal goals).",
            },
            "min_fibre": {
                "type": "number",
                "description": "Minimum fibre in grams.",
            },
            "max_sodium": {
                "type": "number",
                "description": "Maximum sodium in milligrams.",
            },
            "max_sugar": {
                "type": "number",
                "description": "Maximum sugar in grams.",
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Tags the food must have, e.g. ['spicy', 'high_protein'].",
            },
            "dietary_types": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Dietary types the food must match, e.g. ['vegetarian'].",
            },
            "excluded_allergens": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Allergens to exclude, e.g. ['peanuts', 'milk'].",
            },
            "limit": {
                "type": "integer",
                "default": 10,
                "description": "Maximum number of foods to return.",
            },
        },
    },
}


def search_foods(
    db: Session,
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
) -> Dict[str, Any]:
    """
    Execute the search_foods tool.

    This function:
        1) Checks the arguments with Pydantic
        2) Calls FoodService (NO direct database queries here)
        3) Returns structured JSON (as a Python dictionary)
    """

    # Step 1: validate arguments (catch bad input early)
    arguments = SearchFoodsArguments(
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

    # Step 2: call the service layer
    service = FoodService(db)
    result = service.search_foods(
        query=arguments.query,
        food_category=arguments.food_category,
        max_calories=arguments.max_calories,
        min_calories=arguments.min_calories,
        min_protein=arguments.min_protein,
        max_protein=arguments.max_protein,
        max_fat=arguments.max_fat,
        min_fibre=arguments.min_fibre,
        max_sodium=arguments.max_sodium,
        max_sugar=arguments.max_sugar,
        tags=arguments.tags,
        dietary_types=arguments.dietary_types,
        excluded_allergens=arguments.excluded_allergens,
        limit=arguments.limit,
    )

    # Step 3: convert Pydantic model → normal Python dict (JSON-ready)
    return result.model_dump()
