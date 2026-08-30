"""
services/event_service.py
Purpose: All business logic for events — department derivation, duplicate
detection, DB insertion, filtered querying, and the bus-upsert side effect
(so a bus's last known position updates whenever it reports an event).
Keeping this out of api/events.py keeps the route file thin and testable.

Connects to:
- app/api/events.py   -> calls create_event(), get_events(), get_event_by_id()
- app/models/event.py -> the ORM row this writes/reads
- app/models/bus.py   -> upserted as a side effect of create_event()
- app/schemas/event.py -> EventCreate input, PWD_EVENT_TYPES for department logic
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.event import Event
from app.models.bus import Bus
from app.schemas.event import EventCreate, PWD_EVENT_TYPES


class DuplicateEventError(Exception):
    """Raised when an event_id already exists in the database."""
    pass


def map_department(event_type: str) -> str:
    """PWD handles POTHOLE/ROAD_DEFECT, everything else defaults to TRAFFIC."""
    return "PWD" if event_type in PWD_EVENT_TYPES else "TRAFFIC"


def _upsert_bus_position(db: Session, bus_id: str, lat: float, lon: float, timestamp):
    """Create the bus row if it doesn't exist yet, else update its last
    known GPS fix. Called every time a new event arrives (STEP 3: buses)."""
    bus = db.query(Bus).filter(Bus.bus_id == bus_id).first()
    if bus is None:
        bus = Bus(
            bus_id=bus_id,
            route_name=None,
            status="ACTIVE",
            last_latitude=lat,
            last_longitude=lon,
            last_updated=timestamp,
        )
        db.add(bus)
    else:
        bus.last_latitude = lat
        bus.last_longitude = lon
        bus.last_updated = timestamp
        bus.status = "ACTIVE"


def create_event(db: Session, event_in: EventCreate) -> Event:
    """Validate-for-duplicates, insert the event, upsert the bus position.

    Raises DuplicateEventError if event_id already exists.
    """
    existing = db.query(Event).filter(Event.event_id == event_in.event_id).first()
    if existing is not None:
        raise DuplicateEventError(f"event_id '{event_in.event_id}' already exists")

    department = map_department(event_in.event_type)

    db_event = Event(
        event_id=event_in.event_id,
        bus_id=event_in.bus_id,
        camera_id=event_in.camera_id,
        event_type=event_in.event_type,
        confidence=event_in.confidence,
        timestamp=event_in.timestamp,
        latitude=event_in.latitude,
        longitude=event_in.longitude,
        frame_id=event_in.frame_id,
        evidence_path=event_in.evidence_path,
        department=department,
    )

    try:
        db.add(db_event)
        _upsert_bus_position(
            db, event_in.bus_id, event_in.latitude, event_in.longitude, event_in.timestamp
        )
        db.commit()
        db.refresh(db_event)
    except IntegrityError:
        db.rollback()
        raise DuplicateEventError(f"event_id '{event_in.event_id}' already exists")

    return db_event


def get_events(
    db: Session,
    event_type: Optional[str] = None,
    department: Optional[str] = None,
    bus_id: Optional[str] = None,
    limit: int = 200,
) -> list[Event]:
    """Filtered event listing, newest first. Backs GET /events and its
    ?event_type= / ?department= / ?bus_id= query params."""
    query = db.query(Event)

    if event_type:
        query = query.filter(Event.event_type == event_type.upper())
    if department:
        query = query.filter(Event.department == department.upper())
    if bus_id:
        query = query.filter(Event.bus_id == bus_id)

    return query.order_by(Event.timestamp.desc()).limit(limit).all()


def get_event_by_id(db: Session, event_id: str) -> Optional[Event]:
    return db.query(Event).filter(Event.event_id == event_id).first()
