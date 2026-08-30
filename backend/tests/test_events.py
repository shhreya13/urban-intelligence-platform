"""
tests/test_events.py
Purpose: Verifies POST /events (validation + duplicate detection) and
GET /events (listing + filters). Uses the shared isolated test DB from
conftest.py via the `client` fixture.
"""

VALID_EVENT = {
    "event_id": "EVT-0001",
    "bus_id": "BUS-001",
    "camera_id": "FRONT-01",
    "event_type": "POTHOLE",
    "confidence": 0.92,
    "timestamp": "2026-08-26T10:32:14.630",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "frame_id": 1420,
    "evidence_path": "events/EVT-0001.jpg",
}


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_post_event_success(client):
    resp = client.post("/events", json=VALID_EVENT)
    assert resp.status_code == 201
    body = resp.json()
    assert body["event_id"] == "EVT-0001"
    assert body["department"] == "PWD"  # POTHOLE -> PWD


def test_post_event_invalid_confidence(client):
    bad = dict(VALID_EVENT, event_id="EVT-BAD-1", confidence=1.5)
    resp = client.post("/events", json=bad)
    assert resp.status_code == 422


def test_post_event_invalid_event_type(client):
    bad = dict(VALID_EVENT, event_id="EVT-BAD-2", event_type="UFO_SIGHTING")
    resp = client.post("/events", json=bad)
    assert resp.status_code == 422


def test_post_event_invalid_gps(client):
    bad = dict(VALID_EVENT, event_id="EVT-BAD-3", latitude=999)
    resp = client.post("/events", json=bad)
    assert resp.status_code == 422


def test_post_duplicate_event(client):
    client.post("/events", json=VALID_EVENT)
    resp = client.post("/events", json=VALID_EVENT)
    assert resp.status_code == 409


def test_get_events(client):
    client.post("/events", json=VALID_EVENT)
    resp = client.get("/events")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_get_events_filter_by_type(client):
    client.post("/events", json=VALID_EVENT)
    traffic_event = dict(
        VALID_EVENT, event_id="EVT-0002", event_type="TRAFFIC_DENSITY"
    )
    client.post("/events", json=traffic_event)

    resp = client.get("/events", params={"event_type": "POTHOLE"})
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["event_type"] == "POTHOLE"


def test_get_events_filter_by_department(client):
    client.post("/events", json=VALID_EVENT)
    resp = client.get("/events", params={"department": "PWD"})
    assert len(resp.json()) == 1
    resp2 = client.get("/events", params={"department": "TRAFFIC"})
    assert len(resp2.json()) == 0


def test_get_single_event(client):
    client.post("/events", json=VALID_EVENT)
    resp = client.get("/events/EVT-0001")
    assert resp.status_code == 200
    assert resp.json()["event_id"] == "EVT-0001"


def test_get_single_event_not_found(client):
    resp = client.get("/events/EVT-NOPE")
    assert resp.status_code == 404
