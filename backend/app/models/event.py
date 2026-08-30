"""
models/event.py
Purpose: SQLAlchemy ORM model for the `events` table. This is the single
source of truth for what an "event" looks like in SQLite. Events are the
core data unit sent by Person 1 (vehicle), Person 2 (pothole) and Person 3
(GPS/event-engine) via POST /events.

Connects to:
- app/database/database.py  -> Base
- app/schemas/event.py      -> Pydantic schemas mirror these fields
- app/services/event_service.py -> reads/writes rows of this model
- app/api/events.py         -> returns these rows (serialized via schemas)
"""

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Unique business key sent by the AI/event-engine team. Enforced unique
    # so we can detect + reject duplicate submissions (e.g. retried POSTs).
    event_id = Column(String, unique=True, index=True, nullable=False)

    bus_id = Column(String, index=True, nullable=False)
    camera_id = Column(String, nullable=False)

    # e.g. POTHOLE, ROAD_DEFECT, TRAFFIC_DENSITY, CONGESTION, VEHICLE, INCIDENT
    event_type = Column(String, index=True, nullable=False)

    confidence = Column(Float, nullable=False)

    # Timestamp as reported by the event engine (ISO 8601 string, bus-side clock)
    timestamp = Column(DateTime, nullable=False)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    frame_id = Column(Integer, nullable=True)
    evidence_path = Column(String, nullable=True)

    # Derived field: PWD or TRAFFIC. Computed server-side from event_type,
    # never sent by the client. See services/event_service.py -> map_department().
    department = Column(String, index=True, nullable=False)

    # Server-side ingestion time (distinct from the bus-reported `timestamp`)
    created_at = Column(DateTime, server_default=func.now())
