# config.py
# Reads settings from the .env file.
# Think of it as a simple place that stores app configuration.

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Default: SQLite file in the backend folder (no PostgreSQL needed).
    # SQLAlchemy still talks to the database using this URL.
    # Example SQLite:  sqlite:///./food_recommendation.db
    # Example Postgres (optional later):
    #   postgresql://postgres:password@localhost:5432/food_recommendation
    DATABASE_URL: str = "sqlite:///./food_recommendation.db"

    # Ignore other .env keys (OPENAI_API_KEY, etc.) — agents read those separately.
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


# Create one settings object that the whole app can use.
settings = Settings()
