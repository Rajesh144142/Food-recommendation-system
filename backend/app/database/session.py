# session.py
# This file creates the SQLAlchemy engine and session.
# By default we use a local SQLite file (easy to run, no PostgreSQL install).

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Extra settings needed when using SQLite with FastAPI / threads
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite allows only one thread by default.
    # FastAPI can use different threads, so we turn that check off.
    connect_args = {"check_same_thread": False}

# create_engine = open a connection using our DATABASE_URL
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
)

# sessionmaker = a factory that creates new database sessions
# A session is like an open conversation with the database.
SessionLocal = sessionmaker(
    autocommit=False,  # We decide when to save (commit) changes
    autoflush=False,   # Do not auto-write pending changes
    bind=engine,       # Use the engine we created above
)


def get_db():
    """
    Create a database session, give it to the caller,
    then close it when finished.

    This is the safe way to open and close a DB connection.
    """
    db = SessionLocal()
    try:
        yield db  # give the session to whoever called get_db()
    finally:
        db.close()  # always close the session at the end
