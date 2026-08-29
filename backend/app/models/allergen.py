# allergen.py
# This file defines the "allergens" table.

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.base import Base


class Allergen(Base):
    """
    Example rows:
        peanuts
        milk
        gluten
        shellfish
    """

    __tablename__ = "allergens"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    foods = relationship("Food", secondary="food_allergens", back_populates="allergens")
