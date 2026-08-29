# tag.py
# This file defines the "tags" table.
# Tags describe taste, mood, nutrition, or context.

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.base import Base


class Tag(Base):
    """
    Example rows:
        name="spicy",        category="taste"
        name="high_protein", category="nutrition"
        name="comfort_food", category="mood"
        name="quick_meal",   category="context"
    """

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), nullable=True)

    foods = relationship("Food", secondary="food_tags", back_populates="tags")
