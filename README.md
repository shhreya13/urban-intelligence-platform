# Urban Intelligence Platform — SIH26124

AI-Powered Mobile Urban Intelligence Platform Using Public Transport Fleet
(Bharat Electronics Limited, Smart India Hackathon 2026).

This repo contains the **backend** (FastAPI + SQLAlchemy + SQLite) and
**frontend** (React + Vite + Tailwind + Leaflet + Recharts), built and
integrated together by Person 4 + Person 5. The `ai/` and `event-engine/`
folders (Persons 1–3) are separate and integrate with this backend only
through the shared JSON event contract below — no code-level coupling.

## Quick start (both servers)

```bash
# Terminal 1 — backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open http://localhost:5173. The backend auto-creates and seeds
`urban_intelligence.db` with demo buses + events on first run, so the
dashboard has data immediately — Swagger docs at http://localhost:8000/docs.

## Shared event contract (Persons 1–3 send this to POST /events)

```json
{
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
}
```

`event_type` must be one of: `POTHOLE`, `ROAD_DEFECT`, `VEHICLE`,
`TRAFFIC_DENSITY`, `CONGESTION`, `INCIDENT`, `PEDESTRIAN`. The backend
derives `department` automatically (`PWD` for POTHOLE/ROAD_DEFECT,
`TRAFFIC` for everything else) — do not send `department` yourself.

## Final integration checklist

- [x] Backend starts (`uvicorn app.main:app`)
- [x] SQLite database created on startup
- [x] Seed data inserted (5 buses, 7 events, Chennai coordinates)
- [x] `POST /events` works (validated, 201, 409 on duplicate)
- [x] `GET /events` works, with `event_type` / `department` / `bus_id` filters
- [x] `GET /traffic` works
- [x] `GET /buses` works
- [x] CORS works (`http://localhost:5173` whitelisted)
- [x] React starts (`npm run dev`)
- [x] Mock mode works (`VITE_USE_MOCK=true`, or automatic fallback if backend is down)
- [x] React connects to FastAPI (`VITE_USE_MOCK=false`)
- [x] Events appear in EventTable
- [x] Potholes appear on the Leaflet map (amber markers)
- [x] Traffic appears (chart + stat cards)
- [x] Buses appear (🚌 markers with route/status popups)
- [x] Event details modal works (confidence, GPS, timestamp, evidence)
- [x] Evidence displays when `evidence_path` is set
- [x] Traffic view works (`/traffic` page)
- [x] PWD view works (`/pwd` page)
- [x] End-to-end: POST event → SQLite → GET /events → React → EventTable → map marker → click → EventDetails — **verified working**

## Notes

- Backend and frontend were built and tested together, not as separate
  projects — every endpoint above was exercised live (pytest + real HTTP
  requests) before being wired into a corresponding UI feature.
- Folder structure is unchanged from the team's agreed layout. `pages/Traffic.jsx`
  and `pages/PWD.jsx` were added alongside the existing `Dashboard.jsx` /
  `Events.jsx` to satisfy the department-view requirement — this is an
  addition inside the existing `pages/` folder, not a restructure.
- We have only 5 days: no auth, no Postgres/Redis/Kafka, no Kubernetes.
  Keep it this simple until final deployment planning.


cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000

cd frontend && npm install && cp .env.example .env && npm run dev