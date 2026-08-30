"""
api/traffic.py
Purpose: HTTP layer for GET /traffic — vehicle-count/traffic-level summary
consumed by StatCard.jsx (Overview) and TrafficChart.jsx (Traffic view).

Connects to:
- app/services/traffic_service.py -> get_traffic_summary()
- frontend/src/services/api.js    -> getTraffic()
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services import traffic_service

router = APIRouter(prefix="/traffic", tags=["traffic"])


@router.get("")
def get_traffic(db: Session = Depends(get_db)):
    return traffic_service.get_traffic_summary(db)
