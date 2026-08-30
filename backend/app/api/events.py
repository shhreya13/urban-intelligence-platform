"""
api/events.py
Purpose: HTTP layer for events — POST /events (ingestion from Persons 1-3's
event engine) and GET /events, /events/{event_id} (consumed by the React
frontend via services/api.js -> useEvents.js).

Connects to:
- app/services/event_service.py -> all business logic
- app/schemas/event.py           -> request/response validation
- app/database/database.py       -> get_db() session dependency
- frontend/src/services/api.js   -> postEvent(), getEvents(), getEvent()
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.schemas.event import EventCreate, EventOut
from app.services import event_service

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=EventOut, status_code=201)
def post_event(event: EventCreate, db: Session = Depends(get_db)):
    """Ingest one event from the AI/event-engine pipeline.

    - 201 on success
    - 409 if event_id already exists (duplicate-event suppression)
    - 422 automatically on schema validation failure (bad confidence/GPS/type)
    """
    try:
        db_event = event_service.create_event(db, event)
    except event_service.DuplicateEventError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return db_event


@router.get("", response_model=list[EventOut])
def list_events(
    event_type: Optional[str] = Query(None, description="e.g. POTHOLE, TRAFFIC_DENSITY"),
    department: Optional[str] = Query(None, description="PWD or TRAFFIC"),
    bus_id: Optional[str] = Query(None, description="e.g. BUS-001"),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """List events, newest first, with optional filters. Powers EventTable,
    the Leaflet map, and the Traffic/PWD department views."""
    return event_service.get_events(
        db, event_type=event_type, department=department, bus_id=bus_id, limit=limit
    )


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: str, db: Session = Depends(get_db)):
    """Fetch a single event by its business event_id. Powers EventDetails.jsx."""
    db_event = event_service.get_event_by_id(db, event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail=f"event_id '{event_id}' not found")
    return db_event
