"""
services/traffic_service.py
Purpose: Computes the GET /traffic summary. For the 5-day MVP this is
derived from seeded/event data rather than a live vehicle-counter feed.
Structured so Person 1's real vehicle-count output can be swapped in later
by replacing get_traffic_summary()'s internals — the API response shape
(TRAFFIC_SUMMARY schema) stays the same, so the frontend never has to change.

Connects to:
- app/api/traffic.py -> calls get_traffic_summary()
- app/models/event.py -> counts VEHICLE/TRAFFIC_DENSITY/CONGESTION events
"""

from sqlalchemy.orm import Session
from app.models.event import Event

# --- MVP placeholder counts -------------------------------------------------
# Person 1's real detector will eventually report per-class vehicle counts.
# Until then we seed the dashboard with a realistic-looking static baseline,
# but we still fold in the count of any real TRAFFIC_DENSITY events the
# event-engine has already sent, so live incoming data has *some* effect.
_BASELINE = {
    "cars": 72,
    "motorcycles": 41,
    "buses": 12,
    "trucks": 23,
}


def _traffic_level(total_vehicles: int) -> str:
    if total_vehicles < 60:
        return "LOW"
    if total_vehicles < 140:
        return "MODERATE"
    return "HIGH"


def get_traffic_summary(db: Session) -> dict:
    live_traffic_events = (
        db.query(Event)
        .filter(Event.event_type.in_(["TRAFFIC_DENSITY", "CONGESTION"]))
        .count()
    )

    counts = dict(_BASELINE)
    total_vehicles = sum(counts.values()) + live_traffic_events

    return {
        "total_vehicles": total_vehicles,
        "cars": counts["cars"],
        "motorcycles": counts["motorcycles"],
        "buses": counts["buses"],
        "trucks": counts["trucks"],
        "traffic_level": _traffic_level(total_vehicles),
    }
