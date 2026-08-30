"""
app/main.py
Purpose: FastAPI application entrypoint. Wires up CORS (for the Vite dev
server), creates DB tables on startup, seeds demo data, mounts the
events/traffic/buses routers, and exposes GET /health.

Run with: uvicorn app.main:app --reload --port 8000

Connects to:
- app/database/database.py -> init_db()
- app/database/seed.py     -> seed_data()
- app/api/events.py, traffic.py, buses.py -> included routers
- frontend/.env (VITE_API_URL) -> must point at this server's URL
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import init_db
from app.database.seed import seed_data
from app.api import events, traffic, buses, camera

app = FastAPI(
    title="Urban Intelligence Platform API",
    description="SIH26124 - AI-Powered Mobile Urban Intelligence Platform Using Public Transport Fleet",
    version="1.0.0",
)

# CORS: allow the Vite dev server (localhost:5173) to call this API.
# Add any other frontend origins here if the port changes.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    seed_data()


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "service": "urban-intelligence-platform-backend"}


app.include_router(events.router)
app.include_router(traffic.router)
app.include_router(buses.router)
app.include_router(camera.router)


@app.on_event("shutdown")
def on_shutdown():
    camera.shutdown()
