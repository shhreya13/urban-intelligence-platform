"""
tests/conftest.py
Purpose: Single shared in-memory SQLite test database + FastAPI dependency
override, used by every test file. Having one shared engine/override here
(rather than one per test file) avoids each test module clobbering the
others' `app.dependency_overrides[get_db]` on the shared `app` singleton.

Connects to:
- app/main.py -> the shared `app` instance every test file imports
- app/database/database.py -> Base, get_db
- tests/test_events.py, test_traffic.py, test_buses.py -> use `client` fixture
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.database import Base, get_db

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def _fresh_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)
