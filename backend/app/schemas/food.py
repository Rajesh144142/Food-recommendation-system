# food.py (schemas)
# Schemas = the shape of data going IN and OUT of our app.
# We use Pydantic to check that data looks correct.

from typing import List, Optional

from pydantic import BaseModel, Field


# --------------------------------------------------
# INPUT SCHEMA (what the tool accepts)
# --------------------------------------------------


class SearchFoodsArguments(BaseModel):
    """
    These are the optional filters for search_foods.

    Example:
        SearchFoodsArguments(
            max_calories=500,
            min_protein=30,
            tags=["spicy"],
        )
    """

    query: Optional[str] = None
    food_category: Optional[str] = None

    max_calories: Optional[float] = None
    min_calories: Optional[float] = None

    min_protein: Optional[float] = None
    max_protein: Optional[float] = None

    max_fat: Optional[float] = None
    min_fibre: Optional[float] = None
    max_sodium: Optional[float] = None
    max_sugar: Optional[float] = None

    tags: Optional[List[str]] = None
    dietary_types: Optional[List[str]] = None
    excluded_allergens: Optional[List[str]] = None

    # limit is required to have a default value of 10
    limit: int = Field(default=10, ge=1, le=100)


# --------------------------------------------------
# OUTPUT SCHEMAS (what we return as JSON)
# --------------------------------------------------


class NutritionOut(BaseModel):
    """Nutrition numbers for one food."""

    calories: Optional[float] = None
    protein_g: Optional[float] = None
    carbohydrates_g: Optional[float] = None
    fat_g: Optional[float] = None
    fibre_g: Optional[float] = None
    sugar_g: Optional[float] = None
    sodium_mg: Optional[float] = None


class FoodOut(BaseModel):
    """One food item in the search result."""

    id: int
    name: str
    description: Optional[str] = None
    food_category: Optional[str] = None
    preparation_time_minutes: Optional[int] = None

    nutrition: Optional[NutritionOut] = None
    tags: List[str] = []
    dietary_types: List[str] = []
    allergens: List[str] = []


class SearchFoodsResult(BaseModel):
    """The final JSON shape returned by search_foods."""

    foods: List[FoodOut]
