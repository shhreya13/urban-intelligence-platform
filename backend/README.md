# Backend — Urban Intelligence Platform API

FastAPI + SQLAlchemy + SQLite backend for SIH26124.

## Install & Run

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000
```

Visit http://localhost:8000/docs for interactive Swagger UI.
On first startup, `urban_intelligence.db` is created and seeded automatically
with demo buses + events (Chennai-area coordinates).

## Test

```bash
pytest -v
```

## Endpoints

| Method | Path                | Purpose                                   |
|--------|---------------------|--------------------------------------------|
| GET    | /health             | Liveness check                            |
| POST   | /events             | Ingest one event (from event-engine)      |
| GET    | /events             | List events (filters below)               |
| GET    | /events/{event_id}  | Fetch one event                           |
| GET    | /traffic            | Vehicle-count / traffic-level summary     |
| GET    | /buses              | List buses + last known GPS               |

**Filters on GET /events:** `?event_type=POTHOLE`, `?department=PWD`,
`?bus_id=BUS-001` (combinable).

## curl examples

```bash
curl http://localhost:8000/health

curl -X POST http://localhost:8000/events \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "EVT-0001",
    "bus_id": "BUS-001",
    "camera_id": "FRONT-01",
    "event_type": "POTHOLE",
    "confidence": 0.92,
    "timestamp": "2026-08-26T10:32:14.630",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "frame_id": 1420,
    "evidence_path": "events/EVT-0001.jpg"
  }'

curl "http://localhost:8000/events?event_type=POTHOLE"
curl "http://localhost:8000/events?department=TRAFFIC"
curl http://localhost:8000/traffic
curl http://localhost:8000/buses
```

## Notes for Persons 1–3

Send your events to `POST http://localhost:8000/events` in exactly the
shared JSON contract. Do not depend on any internal Python class from this
backend — the JSON contract is the only integration surface.
