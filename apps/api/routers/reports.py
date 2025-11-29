from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from pymongo.database import Database
from ..database import get_mongo_db
from ..models import Report, ReportCreate, ReportRead, PydanticObjectId
from bson import ObjectId # Import ObjectId for querying

router = APIRouter()

@router.post("/reports/", response_model=ReportRead)
def create_report(report: ReportCreate, db: Database = Depends(get_mongo_db)):
    report_dict = report.dict(by_alias=True)
    # Ensure that _id is not passed if it's None, MongoDB will generate it
    if "_id" in report_dict and report_dict["_id"] is None:
        del report_dict["_id"]

    result = db["reports"].insert_one(report_dict)
    # Fetch the created document to include the generated _id
    created_report = db["reports"].find_one({"_id": result.inserted_id})
    if created_report:
        return ReportRead(**created_report)
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create report")

@router.get("/reports/{report_id}", response_model=ReportRead)
def read_report(report_id: PydanticObjectId, db: Database = Depends(get_mongo_db)):
    # PydanticObjectId already validates if it's a valid ObjectId, so we can use it directly
    report = db["reports"].find_one({"_id": ObjectId(str(report_id))}) # Convert to bson.ObjectId for query
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return ReportRead(**report)