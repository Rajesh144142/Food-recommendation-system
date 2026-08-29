# ingredient.py
# This file defines the "ingredients" table.

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database.base import Base


class Ingredient(Base):
    """
    Example rows:
        name="chicken"
        name="rice"
        name="tomato"
    """

    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    foods = relationship("Food", secondary="food_ingredients", back_populates="ingredients")
