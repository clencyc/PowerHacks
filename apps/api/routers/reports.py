from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from ..models import Report, ReportCreate, ReportRead

router = APIRouter()

@router.post("/reports/", response_model=ReportRead)
def create_report(report: ReportCreate, session: Session = Depends(get_session)):
    db_report = Report.from_orm(report)
    session.add(db_report)
    session.commit()
    session.refresh(db_report)
    return db_report

@router.get("/reports/{report_id}", response_model=ReportRead)
def read_report(report_id: int, session: Session = Depends(get_session)):
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
