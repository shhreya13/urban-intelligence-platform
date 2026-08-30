"""
api/buses.py
Purpose: HTTP layer for GET /buses — returns every bus's identity, status
and last known GPS fix, consumed by BusMarker.jsx on the Leaflet map.
Bus rows are upserted automatically inside event_service.create_event(),
so this route is read-only.

Connects to:
- app/models/bus.py            -> ORM rows
- app/schemas/bus.py           -> BusOut response shape
- frontend/src/services/api.js -> getBuses()
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.bus import Bus
from app.schemas.bus import BusOut

router = APIRouter(prefix="/buses", tags=["buses"])


@router.get("", response_model=list[BusOut])
def list_buses(db: Session = Depends(get_db)):
    return db.query(Bus).order_by(Bus.bus_id).all()
