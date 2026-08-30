"""
database/seed.py
Purpose: Populates SQLite with realistic Chennai-area demo data on startup
(multiple buses, multiple potholes, multiple traffic events) so the React
dashboard has something to show immediately, before Persons 1-3's real
pipeline is sending live events. Idempotent — safe to call every startup;
it skips seeding if data already exists.

Connects to:
- app/database/database.py -> SessionLocal
- app/models/event.py, app/models/bus.py -> rows created here
- app/main.py -> calls seed_data() once on startup, after init_db()
"""

from datetime import datetime, timedelta
from app.database.database import SessionLocal
from app.models.event import Event
from app.models.bus import Bus

# Realistic Chennai-area coordinates (roughly along Anna Salai / OMR corridor)
SEED_BUSES = [
    {"bus_id": "BUS-001", "route_name": "Route 21G - T.Nagar to Tambaram", "lat": 13.0827, "lon": 80.2707},
    {"bus_id": "BUS-002", "route_name": "Route 5C - Broadway to Adyar", "lat": 13.0604, "lon": 80.2496},
    {"bus_id": "BUS-003", "route_name": "Route 102 - Anna Nagar to Velachery", "lat": 13.0850, "lon": 80.2101},
    {"bus_id": "BUS-004", "route_name": "Route 18 - Perambur to Guindy", "lat": 13.1143, "lon": 80.2329},
    {"bus_id": "BUS-005", "route_name": "Route 47 - Tondiarpet to OMR", "lat": 13.1230, "lon": 80.2934},
]

SEED_EVENTS = [
    # Potholes (PWD)
    {"event_id": "EVT-1001", "bus_id": "BUS-001", "camera_id": "FRONT-01", "event_type": "POTHOLE",
     "confidence": 0.93, "lat": 13.0827, "lon": 80.2707, "frame_id": 101, "evidence_path": "events/EVT-1001.jpg", "mins_ago": 5},
    {"event_id": "EVT-1002", "bus_id": "BUS-002", "camera_id": "FRONT-01", "event_type": "POTHOLE",
     "confidence": 0.87, "lat": 13.0604, "lon": 80.2496, "frame_id": 202, "evidence_path": "events/EVT-1002.jpg", "mins_ago": 12},
    {"event_id": "EVT-1003", "bus_id": "BUS-003", "camera_id": "FRONT-02", "event_type": "ROAD_DEFECT",
     "confidence": 0.78, "lat": 13.0850, "lon": 80.2101, "frame_id": 305, "evidence_path": "events/EVT-1003.jpg", "mins_ago": 20},
    {"event_id": "EVT-1004", "bus_id": "BUS-004", "camera_id": "FRONT-01", "event_type": "POTHOLE",
     "confidence": 0.95, "lat": 13.1143, "lon": 80.2329, "frame_id": 410, "evidence_path": "events/EVT-1004.jpg", "mins_ago": 3},
    # Traffic (TRAFFIC)
    {"event_id": "EVT-2001", "bus_id": "BUS-001", "camera_id": "FRONT-01", "event_type": "TRAFFIC_DENSITY",
     "confidence": 0.81, "lat": 13.0700, "lon": 80.2600, "frame_id": 150, "evidence_path": None, "mins_ago": 8},
    {"event_id": "EVT-2002", "bus_id": "BUS-005", "camera_id": "FRONT-01", "event_type": "CONGESTION",
     "confidence": 0.89, "lat": 13.1230, "lon": 80.2934, "frame_id": 220, "evidence_path": None, "mins_ago": 15},
    {"event_id": "EVT-2003", "bus_id": "BUS-003", "camera_id": "FRONT-01", "event_type": "TRAFFIC_DENSITY",
     "confidence": 0.74, "lat": 13.0900, "lon": 80.2200, "frame_id": 260, "evidence_path": None, "mins_ago": 25},
]


def seed_data():
    db = SessionLocal()
    try:
        if db.query(Event).count() > 0 or db.query(Bus).count() > 0:
            return  # already seeded

        now = datetime.utcnow()

        for b in SEED_BUSES:
            db.add(
                Bus(
                    bus_id=b["bus_id"],
                    route_name=b["route_name"],
                    status="ACTIVE",
                    last_latitude=b["lat"],
                    last_longitude=b["lon"],
                    last_updated=now,
                )
            )

        for e in SEED_EVENTS:
            department = "PWD" if e["event_type"] in ("POTHOLE", "ROAD_DEFECT") else "TRAFFIC"
            db.add(
                Event(
                    event_id=e["event_id"],
                    bus_id=e["bus_id"],
                    camera_id=e["camera_id"],
                    event_type=e["event_type"],
                    confidence=e["confidence"],
                    timestamp=now - timedelta(minutes=e["mins_ago"]),
                    latitude=e["lat"],
                    longitude=e["lon"],
                    frame_id=e["frame_id"],
                    evidence_path=e["evidence_path"],
                    department=department,
                )
            )

        db.commit()
        print(f"Seeded {len(SEED_BUSES)} buses and {len(SEED_EVENTS)} events.")
    finally:
        db.close()
