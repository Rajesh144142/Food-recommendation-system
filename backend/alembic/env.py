# Alembic env.py
# This file tells Alembic:
#   1) which database to connect to
#   2) which SQLAlchemy models to look at

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.config import settings
from app.database.base import Base

# Import all models so Alembic can see every table.
from app.models import (  # noqa: F401
    Allergen,
    DietaryType,
    Food,
    FoodAllergen,
    FoodDietaryType,
    FoodIngredient,
    FoodNutrition,
    FoodTag,
    Ingredient,
    Tag,
)

# This is the Alembic Config object.
config = context.config

# Read logging settings from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use DATABASE_URL from our app settings (.env), not the hardcoded alembic.ini value.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# target_metadata = all tables defined on Base
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    This generates SQL without connecting to the database.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    This connects to PostgreSQL and applies the changes.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
