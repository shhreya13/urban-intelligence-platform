"""
schemas/event.py
Purpose: Pydantic models used for request validation (EventCreate — the
exact shared contract Persons 1/2/3 send) and response serialization
(EventOut). This is where confidence/GPS/type validation rules live.

Connects to:
- app/api/events.py         -> uses EventCreate to validate POST body,
                                returns list[EventOut] / EventOut
- app/services/event_service.py -> receives a validated EventCreate,
                                returns Event ORM rows that FastAPI
                                serializes using EventOut (orm_mode)
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

# Allowed event types for the 5-day MVP. Extend here if Persons 1-3 add more.
VALID_EVENT_TYPES = {
    "POTHOLE",
    "ROAD_DEFECT",
    "VEHICLE",
    "TRAFFIC_DENSITY",
    "CONGESTION",
    "INCIDENT",
    "PEDESTRIAN",
}

# Which event_types belong to which department (server-derived, never sent
# by the client). Anything not listed defaults to TRAFFIC.
PWD_EVENT_TYPES = {"POTHOLE", "ROAD_DEFECT"}


class EventCreate(BaseModel):
    """Exact shared contract from Persons 1/2/3 (event-engine)."""

    event_id: str = Field(..., min_length=1, examples=["EVT-0001"])
    bus_id: str = Field(..., min_length=1, examples=["BUS-001"])
    camera_id: str = Field(..., min_length=1, examples=["FRONT-01"])
    event_type: str = Field(..., examples=["POTHOLE"])
    confidence: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    frame_id: Optional[int] = None
    evidence_path: Optional[str] = None

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, v: str) -> str:
        v_upper = v.upper()
        if v_upper not in VALID_EVENT_TYPES:
            raise ValueError(
                f"event_type must be one of {sorted(VALID_EVENT_TYPES)}, got '{v}'"
            )
        return v_upper

    @field_validator("bus_id", "camera_id", "event_id")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be blank")
        return v.strip()


class EventOut(BaseModel):
    """Response shape for a stored event, including server-derived fields."""

    id: int
    event_id: str
    bus_id: str
    camera_id: str
    event_type: str
    confidence: float
    timestamp: datetime
    latitude: float
    longitude: float
    frame_id: Optional[int] = None
    evidence_path: Optional[str] = None
    department: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # allows EventOut.model_validate(orm_row)
