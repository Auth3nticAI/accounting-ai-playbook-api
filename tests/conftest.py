"""Test fixtures — runs each test against an isolated in-memory SQLite DB.

Pattern: override the get_db dependency so each test gets a fresh session
backed by SQLite, no Postgres or Docker needed in CI.
"""

import os
import sys
from pathlib import Path

# Make the project root importable
sys.path.insert(0, str(Path(__file__).parent.parent))

# Force SQLite for tests BEFORE database.py is imported
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app


@pytest.fixture
def db_session():
    """Each test gets a brand-new in-memory SQLite DB."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """FastAPI test client with the DB dependency overridden."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
