from fastapi import APIRouter, Depends
from pymongo.database import Database # Import Database type
from ..database import get_mongo_db
from ..models import AnalyticsData # Still import AnalyticsData for type hinting if needed

router = APIRouter()

@router.get("/analytics/overview")
def get_analytics_overview(db: Database = Depends(get_mongo_db)): # Changed dependency injection
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