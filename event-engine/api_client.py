"""
FastAPI client -- Person 3 module.

Sends a generated event to Person 4's backend: POST {BACKEND_URL}.
Must NEVER crash the program if the backend is unavailable -- in that
case it prints a clear message, saves the event locally, and returns a
status dict describing what happened instead.
"""

import json
import os

import requests

import config


def send_event(event: dict, backend_url: str = None) -> dict:
    """
    Returns a status dict:
        {"status": "sent", "response": <backend JSON or None>}
        {"status": "backend_unavailable", "reason": "<error message>"}

    On failure the event is always appended to config.OUTPUT_FILE so
    nothing is lost even if the backend never comes up.
    """
    backend_url = backend_url or config.BACKEND_URL

    try:
        response = requests.post(backend_url, json=event, timeout=config.BACKEND_TIMEOUT_SECONDS)
        response.raise_for_status()
        print(f"[api_client] Sent {event['event_id']} to backend ({backend_url}) -> HTTP {response.status_code}")
        try:
            return {"status": "sent", "response": response.json()}
        except ValueError:
            return {"status": "sent", "response": None}

    except requests.exceptions.RequestException as exc:
        print(f"[api_client] WARNING: backend unavailable at {backend_url}: {exc}")
        print("[api_client] Event NOT lost -- saving it locally instead.")
        _save_locally(event)
        return {"status": "backend_unavailable", "reason": str(exc)}


def _save_locally(event: dict):
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    with open(config.OUTPUT_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")


if __name__ == "__main__":
    # Manual check: point at a port nothing is listening on, on purpose.
    dummy_event = {
        "event_id": "EVT-0000", "bus_id": "BUS-001", "camera_id": "FRONT-01",
        "event_type": "POTHOLE", "confidence": 0.5, "timestamp": "2026-08-30T00:00:00.000",
        "latitude": 13.0827, "longitude": 80.2707, "frame_id": 0, "evidence_path": None,
    }
    print(send_event(dummy_event, backend_url="http://localhost:59999/events"))
