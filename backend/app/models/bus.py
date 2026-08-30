"""
models/bus.py
Purpose: SQLAlchemy ORM model for the `buses` table. Tracks each bus's
identity, route, status and last known GPS fix so the frontend map can
render live bus markers (BusMarker.jsx).

Connects to:
- app/database/database.py -> Base
- app/schemas/bus.py        -> Pydantic schema mirrors these fields
- app/services/event_service.py -> updates a bus's last position whenever
  a new event arrives from that bus (upsert)
- app/api/buses.py          -> returns these rows
"""

from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database.database import Base


class Bus(Base):
    __tablename__ = "buses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    bus_id = Column(String, unique=True, index=True, nullable=False)
    route_name = Column(String, nullable=True)

    # ACTIVE / IDLE / OFFLINE — simple status for the MVP
    status = Column(String, default="ACTIVE")

    last_latitude = Column(Float, nullable=True)
    last_longitude = Column(Float, nullable=True)
    last_updated = Column(DateTime, nullable=True)
