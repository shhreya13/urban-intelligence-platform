# Frontend — Urban Intelligence Platform Dashboard

React + Vite + Tailwind + Leaflet + Recharts dashboard for SIH26124.

## Install & Run

```bash
cd frontend
npm install
cp .env.example .env      # adjust VITE_API_URL / VITE_USE_MOCK if needed
npm run dev
```

Visit http://localhost:5173

## Mock mode (frontend works without the backend)

Set `VITE_USE_MOCK=true` in `.env` to always use `src/data/mockEvents.js`.
With `VITE_USE_MOCK=false` (default), the app calls the live FastAPI backend
and **automatically falls back to demo data** if it's unreachable — you'll
see a "Backend unavailable — using demo data" banner, and the UI keeps
working either way.

## Structure

- `services/api.js` — the only file that makes HTTP calls. Everything else
  (hooks, pages) goes through it.
- `hooks/useEvents.js` — fetch/loading/error/refresh for events, reused by
  every page.
- `pages/Dashboard.jsx` — Overview (stat cards, GIS map, traffic chart, recent events)
- `pages/Traffic.jsx` — Traffic department view
- `pages/PWD.jsx` — PWD (Public Works) department view
- `pages/Events.jsx` — all events with type/department/bus filters
- `map/MapView.jsx` + `EventMarker.jsx` + `BusMarker.jsx` — Leaflet GIS map

## Connecting to the real backend

1. Start the backend (see `../backend/README.md`) — it listens on `:8000`
   and allows CORS from `:5173` by default.
2. Set `VITE_USE_MOCK=false` and `VITE_API_URL=http://localhost:8000` in `.env`.
3. Restart `npm run dev`. The Navbar's status dot turns green when connected.
