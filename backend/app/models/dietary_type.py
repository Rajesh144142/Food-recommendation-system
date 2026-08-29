# dietary_type.py
# This file defines the "dietary_types" table.

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.base import Base


class DietaryType(Base):
    """
    Example rows:
        vegetarian
        vegan
        non_vegetarian
        gluten_free
        dairy_free
    """

    __tablename__ = "dietary_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    foods = relationship("Food", secondary="food_dietary_types", back_populates="dietary_types")
