"""
tests/test_buses.py
Purpose: Verifies GET /buses, and that posting an event upserts the
reporting bus's last known position (used by BusMarker.jsx on the map).
"""


def test_get_buses_empty(client):
    resp = client.get("/buses")
    assert resp.status_code == 200
    assert resp.json() == []


def test_bus_upserted_on_event(client):
    event = {
        "event_id": "EVT-9001",
        "bus_id": "BUS-099",
        "camera_id": "FRONT-01",
        "event_type": "POTHOLE",
        "confidence": 0.9,
        "timestamp": "2026-08-26T10:32:14.630",
        "latitude": 13.05,
        "longitude": 80.25,
        "frame_id": 1,
        "evidence_path": None,
    }
    client.post("/events", json=event)

    resp = client.get("/buses")
    assert resp.status_code == 200
    buses = resp.json()
    assert len(buses) == 1
    assert buses[0]["bus_id"] == "BUS-099"
    assert buses[0]["last_latitude"] == 13.05
