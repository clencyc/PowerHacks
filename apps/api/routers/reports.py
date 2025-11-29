from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlmodel import Session, select, func, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import json
from cryptography.fernet import Fernet
import os

from database import get_session
from models import (
    Report, ReportCreate, ReportRead, ReportUpdate, 
    IncidentStatus, IncidentSeverity, ReportSource,
    AuditLog, DashboardStats
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize encryption
ENCRYPTION_KEY = os.environ.get("REPORT_ENCRYPTION_KEY")
if ENCRYPTION_KEY:
    cipher_suite = Fernet(ENCRYPTION_KEY.encode() if len(ENCRYPTION_KEY) == 44 else Fernet.generate_key())
else:
    cipher_suite = Fernet(Fernet.generate_key())
    logger.warning("Using generated encryption key. Set REPORT_ENCRYPTION_KEY in production.")

def log_audit_action(session: Session, action: str, user_id: str = None, report_id: int = None, details: dict = None):
    """Log audit trail for admin actions"""
    audit_entry = AuditLog(
        action=action,
        user_id=user_id, 
        report_id=report_id,
        details=details or {}
    )
    session.add(audit_entry)

# REPORT CRUD OPERATIONS

@router.post("/reports/", response_model=ReportRead)
def create_report(
    report: ReportCreate, 
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """Create a new anonymous report"""
    try:
        # Create report with current timestamp
        db_report = Report(**report.dict())
        db_report.created_at = datetime.utcnow()
        db_report.updated_at = datetime.utcnow()
        
        session.add(db_report)
        session.commit()
        session.refresh(db_report)
        
        # Log audit action
        log_audit_action(
            session, 
            "report_created", 
            details={"report_id": db_report.id, "source": report.source}
        )
        session.commit()
        
        # Add background task to analyze severity if not set
        if not db_report.severity:
            background_tasks.add_task(analyze_report_severity, db_report.id)
        
        logger.info(f"New report created: {db_report.id}")
        return db_report
        
    except Exception as e:
        logger.error(f"Error creating report: {e}")
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to create report")

@router.get("/reports/", response_model=List[ReportRead])
def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    status: Optional[IncidentStatus] = None,
    severity: Optional[IncidentSeverity] = None,
    source: Optional[ReportSource] = None,
    days: Optional[int] = Query(None, description="Reports from last N days"),
    session: Session = Depends(get_session)
):
    """List reports with filtering options"""
    try:
        query = select(Report)
        
        # Apply filters
        filters = []
        
        if status:
            filters.append(Report.status == status)
        if severity:
            filters.append(Report.severity == severity)  
        if source:
            filters.append(Report.source == source)
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            filters.append(Report.created_at >= cutoff_date)
            
        if filters:
            query = query.where(and_(*filters))
            
        # Order by creation date (newest first)
        query = query.order_by(Report.created_at.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        reports = session.exec(query).all()
        return reports
        
    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve reports")

@router.get("/reports/{report_id}", response_model=ReportRead)
def get_report(report_id: int, session: Session = Depends(get_session)):
    """Get a specific report by ID"""
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.patch("/reports/{report_id}", response_model=ReportRead) 
def update_report(
    report_id: int, 
    update_data: ReportUpdate,
    reviewer_id: str = Query(..., description="ID of the reviewing admin"),
    session: Session = Depends(get_session)
):
    """Update report status and add review notes"""
    try:
        report = session.get(Report, report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Store old values for audit
        old_status = report.status
        old_severity = report.severity
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(report, field, value)
            
        report.updated_at = datetime.utcnow()
        
        # Log audit action
        log_audit_action(
            session,
            "report_updated",
            user_id=reviewer_id,
            report_id=report_id,
            details={
                "old_status": old_status,
                "new_status": update_data.status,
                "old_severity": old_severity, 
                "new_severity": update_data.severity,
                "review_notes": update_data.review_notes
            }
        )
        
        session.add(report)
        session.commit()
        session.refresh(report)
        
        logger.info(f"Report {report_id} updated by {reviewer_id}")
        return report
        
    except Exception as e:
        logger.error(f"Error updating report {report_id}: {e}")
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to update report")

@router.delete("/reports/{report_id}")
def delete_report(
    report_id: int,
    admin_id: str = Query(..., description="ID of the admin performing deletion"),
    session: Session = Depends(get_session)
):
    """Delete a report (admin only, for GDPR compliance)"""
    try:
        report = session.get(Report, report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Log audit action before deletion
        log_audit_action(
            session,
            "report_deleted", 
            user_id=admin_id,
            report_id=report_id,
            details={"reason": "Admin deletion or GDPR request"}
        )
        
        session.delete(report)
        session.commit()
        
        logger.info(f"Report {report_id} deleted by admin {admin_id}")
        return {"message": "Report deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting report {report_id}: {e}")
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete report")

# ADMIN DASHBOARD ENDPOINTS

@router.get("/reports/stats/dashboard", response_model=DashboardStats)
def get_dashboard_stats(session: Session = Depends(get_session)):
    """Get dashboard statistics for admin panel"""
    try:
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        
        # Basic counts
        total_reports = session.exec(select(func.count(Report.id))).first()
        pending_reports = session.exec(
            select(func.count(Report.id)).where(Report.status == IncidentStatus.PENDING)
        ).first()
        high_severity_reports = session.exec(
            select(func.count(Report.id)).where(Report.severity == IncidentSeverity.HIGH)
        ).first()
        reports_this_week = session.exec(
            select(func.count(Report.id)).where(Report.created_at >= week_ago)
        ).first()
        
        # Resolution rate
        total_non_pending = session.exec(
            select(func.count(Report.id)).where(Report.status != IncidentStatus.PENDING)
        ).first()
        resolution_rate = (total_non_pending / total_reports * 100) if total_reports > 0 else 0
        
        # Top categories (this would need to be implemented based on your categories structure)
        top_categories = [
            {"name": "Sexual Harassment", "count": 5}, 
            {"name": "Discrimination", "count": 3},
            {"name": "Verbal Abuse", "count": 2}
        ]  # Placeholder - implement based on your needs
        
        return DashboardStats(
            total_reports=total_reports or 0,
            pending_reports=pending_reports or 0, 
            high_severity_reports=high_severity_reports or 0,
            reports_this_week=reports_this_week or 0,
            resolution_rate=round(resolution_rate, 2),
            top_categories=top_categories
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard statistics")

# UTILITY FUNCTIONS

def decrypt_report_content(encrypted_blob: str) -> dict:
    """Decrypt report content for admin viewing"""
    try:
        decrypted_data = cipher_suite.decrypt(encrypted_blob.encode())
        return json.loads(decrypted_data.decode())
    except Exception as e:
        logger.error(f"Error decrypting report: {e}")
        return {"error": "Unable to decrypt report content"}

def analyze_report_severity(report_id: int):
    """Background task to analyze report severity"""
    # This would integrate with your detection service
    # For now, it's a placeholder
    logger.info(f"Analyzing severity for report {report_id}")
    # Implementation would go here
