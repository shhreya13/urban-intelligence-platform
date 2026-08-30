"""
database.py
Purpose: Creates the SQLAlchemy engine, session factory, and declarative Base
for the Urban Intelligence Platform backend. Every model (event.py, bus.py)
imports Base from here. Every route/service gets a DB session via get_db().

Connects to:
- app/models/event.py, app/models/bus.py  -> import Base
- app/database/seed.py                    -> imports SessionLocal, engine
- app/main.py                             -> calls init_db() on startup
- app/api/*.py                            -> uses Depends(get_db)
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./urban_intelligence.db")

# check_same_thread=False is required for SQLite when used with FastAPI's
# threaded request handling.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Called once on app startup (main.py)."""
    # Import models here (not at module top) to avoid circular imports,
    # since models import Base from this same file.
    from app.models import event, bus  # noqa: F401

    Base.metadata.create_all(bind=engine)
