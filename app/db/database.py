"""
Database engine + session setup.

Connection string comes from the DATABASE_URL environment variable —
never hardcode credentials here. In dev, docker-compose.yml sets it via
the .env pattern / shell export before `uvicorn app.main:app` runs. See
docker-compose.yml at the repo root for the matching dev Postgres service.
"""

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    # Falls back to the docker-compose dev defaults so `uvicorn` still boots
    # without extra setup during the hackathon — override in real deploys.
    "postgresql+psycopg2://lprdev:lprdevpass@localhost:5432/learning_path_recommender",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator:
    """FastAPI dependency — yields one session per request, always closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Create tables if they don't exist yet. Called once on app startup.

    Hackathon-speed choice: no Alembic migrations. If this goes to
    production, replace this with a proper Alembic migration chain so
    schema changes are versioned instead of inferred from the models.
    """
    from app.db import models  # noqa: F401  (ensure models are registered on Base)

    Base.metadata.create_all(bind=engine)