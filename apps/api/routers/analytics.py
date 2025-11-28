from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..database import get_session
from ..models import AnalyticsData

router = APIRouter()

@router.get("/analytics/overview")
def get_analytics_overview(session: Session = Depends(get_session)):
    # Mock data for now, would aggregate from DB
    return {
        "total_reports": 150,
        "resolved_reports": 120,
        "pending_reports": 30,
        "incidents_by_category": [
            {"name": "Harassment", "value": 40},
            {"name": "Microaggression", "value": 80},
            {"name": "Other", "value": 30},
        ]
    }
