# Import all models in one place.
# Alembic needs this so it can "see" every table when creating migrations.

from app.models.food import Food, FoodAllergen, FoodDietaryType, FoodIngredient, FoodTag
from app.models.nutrition import FoodNutrition
from app.models.tag import Tag
from app.models.ingredient import Ingredient
from app.models.dietary_type import DietaryType
from app.models.allergen import Allergen

__all__ = [
    "Food",
    "FoodTag",
    "FoodIngredient",
    "FoodDietaryType",
    "FoodAllergen",
    "FoodNutrition",
    "Tag",
    "Ingredient",
    "DietaryType",
    "Allergen",
]
