# nutrition.py
# This file defines the "food_nutrition" table.
# One food has exactly one nutrition record.

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database.base import Base


class FoodNutrition(Base):
    """
    Stores nutrition values for one food.

    Example:
        calories = 450
        protein_g = 40
    """

    __tablename__ = "food_nutrition"

    id = Column(Integer, primary_key=True, index=True)
    food_id = Column(Integer, ForeignKey("foods.id"), unique=True, nullable=False)

    calories = Column(Float, nullable=True)
    protein_g = Column(Float, nullable=True)
    carbohydrates_g = Column(Float, nullable=True)
    fat_g = Column(Float, nullable=True)
    fibre_g = Column(Float, nullable=True)   # UK spelling: fibre
    sugar_g = Column(Float, nullable=True)
    sodium_mg = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Link back to the Food model
    food = relationship("Food", back_populates="nutrition")
