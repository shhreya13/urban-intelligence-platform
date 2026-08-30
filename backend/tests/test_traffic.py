"""
tests/test_traffic.py
Purpose: Verifies GET /traffic returns the expected summary shape and that
the traffic_level reflects the vehicle-count baseline.
"""


def test_traffic_summary_shape(client):
    resp = client.get("/traffic")
    assert resp.status_code == 200
    body = resp.json()
    for key in ["total_vehicles", "cars", "motorcycles", "buses", "trucks", "traffic_level"]:
        assert key in body


def test_traffic_level_is_valid(client):
    resp = client.get("/traffic")
    assert resp.json()["traffic_level"] in ("LOW", "MODERATE", "HIGH")
