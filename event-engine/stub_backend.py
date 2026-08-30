"""
OPTIONAL -- a tiny stub FastAPI server so Person 3 can prove the FastAPI
interface (api_client.send_event) actually works, WITHOUT waiting on
Person 4's real backend to be finished.

This is NOT Person 4's real backend (no database, no persistence beyond a
Python list in memory) -- it is a local testing double that accepts
exactly the same POST /events shape Person 4's real backend will accept.

Requires two extra packages that are OPTIONAL for the rest of this project
(not in requirements.txt, since the MVP itself doesn't need them):

    pip install fastapi "uvicorn[standard]"

Run:
    uvicorn stub_backend:app --port 8000

Then in another terminal:
    python main.py
    python test_engine.py

Visit http://localhost:8000/docs to see events land, or GET /events.
"""

from fastapi import FastAPI

app = FastAPI(title="Person 3 -- stub backend (NOT Person 4's real backend)")
_received = []


@app.get("/health")
def health():
    return {"status": "ok", "note": "this is the STUB backend, not Person 4's real one"}


@app.post("/events")
def create_event(event: dict):
    _received.append(event)
    print(f"[stub_backend] received: {event.get('event_id')}  {event.get('event_type')}  "
          f"({event.get('latitude')}, {event.get('longitude')})")
    return event


@app.get("/events")
def list_events():
    return _received
