"""
schemas/bus.py
Purpose: Response schema for GET /buses. Buses are upserted internally
(via event ingestion or seed data) — there is no POST /buses in the MVP,
so only an output schema is needed.

Connects to:
- app/api/buses.py -> returns list[BusOut]
- app/models/bus.py -> ORM fields mirrored here
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class BusOut(BaseModel):
    id: int
    bus_id: str
    route_name: Optional[str] = None
    status: str
    last_latitude: Optional[float] = None
    last_longitude: Optional[float] = None
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True
