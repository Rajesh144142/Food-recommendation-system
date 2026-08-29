# food_repository.py
# Repository = the ONLY place that talks to PostgreSQL with SQLAlchemy.
# It builds a dynamic query based on optional filters.

from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.allergen import Allergen
from app.models.dietary_type import DietaryType
from app.models.food import Food
from app.models.nutrition import FoodNutrition
from app.models.tag import Tag


class FoodRepository:
    """
    This class runs database queries for foods.

    Important:
        - The tool does NOT call this class.
        - The service calls this class.
    """

    def __init__(self, db: Session):
        # Save the database session so we can use it in methods.
        self.db = db

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
    ) -> List[Food]:
        """
        Build a SQLAlchemy query step by step.
        Only add a filter when that argument is given.
        """

        # Start with: SELECT foods ... and also load related data
        # joinedload = load nutrition/tags/etc in the same query (faster)
        db_query = self.db.query(Food).options(
            joinedload(Food.nutrition),
            joinedload(Food.tags),
            joinedload(Food.dietary_types),
            joinedload(Food.allergens),
        )

        # ------------------------------------------
        # 1) Text search on name or description
        # ------------------------------------------
        if query:
            # ilike = case-insensitive "contains" search
            # Example: query="chicken" matches "Grilled Chicken Bowl"
            like_pattern = f"%{query}%"
            db_query = db_query.filter(
                (Food.name.ilike(like_pattern)) | (Food.description.ilike(like_pattern))
            )

        # ------------------------------------------
        # 2) Filter by food category
        # ------------------------------------------
        if food_category:
            db_query = db_query.filter(Food.food_category == food_category)

        # ------------------------------------------
        # 3) Nutrition filters
        #    We join food_nutrition only when needed.
        # ------------------------------------------
        needs_nutrition_join = any(
            value is not None
            for value in [
                max_calories,
                min_calories,
                min_protein,
                max_protein,
                max_fat,
                min_fibre,
                max_sodium,
                max_sugar,
            ]
        )

        if needs_nutrition_join:
            db_query = db_query.join(FoodNutrition)

            if max_calories is not None:
                db_query = db_query.filter(FoodNutrition.calories <= max_calories)

            if min_calories is not None:
                db_query = db_query.filter(FoodNutrition.calories >= min_calories)

            if min_protein is not None:
                db_query = db_query.filter(FoodNutrition.protein_g >= min_protein)

            if max_protein is not None:
                db_query = db_query.filter(FoodNutrition.protein_g <= max_protein)

            if max_fat is not None:
                db_query = db_query.filter(FoodNutrition.fat_g <= max_fat)

            if min_fibre is not None:
                db_query = db_query.filter(FoodNutrition.fibre_g >= min_fibre)

            if max_sodium is not None:
                db_query = db_query.filter(FoodNutrition.sodium_mg <= max_sodium)

            if max_sugar is not None:
                db_query = db_query.filter(FoodNutrition.sugar_g <= max_sugar)

        # ------------------------------------------
        # 4) Must have ALL given tags
        #    Example: tags=["spicy"] → food must have "spicy"
        # ------------------------------------------
        if tags:
            for tag_name in tags:
                db_query = db_query.filter(
                    Food.tags.any(Tag.name == tag_name)
                )

        # ------------------------------------------
        # 5) Must have ALL given dietary types
        #    Example: dietary_types=["vegetarian"]
        # ------------------------------------------
        if dietary_types:
            for dietary_name in dietary_types:
                db_query = db_query.filter(
                    Food.dietary_types.any(DietaryType.name == dietary_name)
                )

        # ------------------------------------------
        # 6) Exclude foods that contain any of these allergens
        #    Example: excluded_allergens=["peanuts"]
        # ------------------------------------------
        if excluded_allergens:
            for allergen_name in excluded_allergens:
                db_query = db_query.filter(
                    ~Food.allergens.any(Allergen.name == allergen_name)
                )

        # ------------------------------------------
        # 7) Limit how many rows we return
        # ------------------------------------------
        db_query = db_query.limit(limit)

        # .all() runs the query and returns a list of Food objects
        return db_query.all()
