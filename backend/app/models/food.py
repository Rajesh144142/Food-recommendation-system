# food.py
# This file defines the "foods" table and the join tables
# that connect foods to tags, ingredients, dietary types, and allergens.

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.base import Base


# --------------------------------------------------
# JOIN TABLES (many-to-many links)
# --------------------------------------------------
# These tables only store IDs that connect two tables.
# Example: food_id=1 and tag_id=3 means food 1 has tag 3.


class FoodTag(Base):
    """Links a food to a tag. Primary key = food_id + tag_id"""

    __tablename__ = "food_tags"

    food_id = Column(Integer, ForeignKey("foods.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)


class FoodIngredient(Base):
    """Links a food to an ingredient, with quantity and unit."""

    __tablename__ = "food_ingredients"

    food_id = Column(Integer, ForeignKey("foods.id"), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), primary_key=True)
    quantity = Column(String(50), nullable=True)  # e.g. "100"
    unit = Column(String(50), nullable=True)      # e.g. "g"


class FoodDietaryType(Base):
    """Links a food to a dietary type. Primary key = food_id + dietary_type_id"""

    __tablename__ = "food_dietary_types"

    food_id = Column(Integer, ForeignKey("foods.id"), primary_key=True)
    dietary_type_id = Column(Integer, ForeignKey("dietary_types.id"), primary_key=True)


class FoodAllergen(Base):
    """Links a food to an allergen. Primary key = food_id + allergen_id"""

    __tablename__ = "food_allergens"

    food_id = Column(Integer, ForeignKey("foods.id"), primary_key=True)
    allergen_id = Column(Integer, ForeignKey("allergens.id"), primary_key=True)


# --------------------------------------------------
# MAIN FOOD TABLE
# --------------------------------------------------


class Food(Base):
    """
    One row in this table = one food item.

    Example:
        name = "Grilled Chicken Bowl"
        food_category = "main_course"
    """

    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    food_category = Column(String(100), nullable=True)
    image_url = Column(String(500), nullable=True)
    preparation_time_minutes = Column(Integer, nullable=True)
    serving_size = Column(String(50), nullable=True)
    serving_unit = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationship = easy way to access related data from Python
    # Example: food.nutrition, food.tags, food.allergens
    nutrition = relationship("FoodNutrition", back_populates="food", uselist=False)
    tags = relationship("Tag", secondary="food_tags", back_populates="foods")
    ingredients = relationship("Ingredient", secondary="food_ingredients", back_populates="foods")
    dietary_types = relationship("DietaryType", secondary="food_dietary_types", back_populates="foods")
    allergens = relationship("Allergen", secondary="food_allergens", back_populates="foods")
