# base.py
# This file creates the base class for all database tables.
# Every model (Food, Tag, etc.) will inherit from this Base.

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base is the parent class for all our database models.

    Example:
        class Food(Base):
            ...
    """
    pass
