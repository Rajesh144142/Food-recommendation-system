# food_service.py
# Service = business logic layer.
# The tool calls the service.
# The service calls the repository.
# The service does NOT write SQL itself.

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.food import Food
from app.repositories.food_repository import FoodRepository
from app.schemas.food import FoodOut, NutritionOut, SearchFoodsResult


class FoodService:
    """
    This class contains the business logic for foods.

    Flow:
        Tool  →  FoodService  →  FoodRepository  →  PostgreSQL
    """

    def __init__(self, db: Session):
        # Create a repository using the same database session.
        self.repository = FoodRepository(db)

    def search_foods(
        self,
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
    ) -> SearchFoodsResult:
        """
        1) Ask the repository for matching Food rows.
        2) Convert those rows into clean JSON-ready objects.
        3) Return the structured result.
        """

        # Step 1: get raw Food objects from the database
        foods = self.repository.search_foods(
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

        # Step 2: convert each Food object into a FoodOut schema
        food_list = [self._to_food_out(food) for food in foods]

        # Step 3: wrap the list in the final result shape
        return SearchFoodsResult(foods=food_list)

    def _to_food_out(self, food: Food) -> FoodOut:
        """
        Convert one SQLAlchemy Food object into a Pydantic FoodOut object.

        Why?
            The LLM / API should get clean JSON, not database objects.
        """

        # Convert nutrition if it exists
        nutrition = None
        if food.nutrition is not None:
            nutrition = NutritionOut(
                calories=food.nutrition.calories,
                protein_g=food.nutrition.protein_g,
                carbohydrates_g=food.nutrition.carbohydrates_g,
                fat_g=food.nutrition.fat_g,
                fibre_g=food.nutrition.fibre_g,
                sugar_g=food.nutrition.sugar_g,
                sodium_mg=food.nutrition.sodium_mg,
            )

        # Convert related lists into simple string lists
        tag_names = [tag.name for tag in food.tags]
        dietary_names = [d.name for d in food.dietary_types]
        allergen_names = [a.name for a in food.allergens]

        return FoodOut(
            id=food.id,
            name=food.name,
            description=food.description,
            food_category=food.food_category,
            preparation_time_minutes=food.preparation_time_minutes,
            nutrition=nutrition,
            tags=tag_names,
            dietary_types=dietary_names,
            allergens=allergen_names,
        )
