from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlmodel import Field, SQLModel, JSON, Column
from pydantic import BaseModel
from enum import Enum

# ENUMS
class IncidentStatus(str, Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review" 
    RESOLVED = "resolved"
    ESCALATED = "escalated"

class IncidentSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ReportSource(str, Enum):
    SLACK = "slack"
    WEB = "web"
    EMAIL = "email"
    PHONE = "phone"

# MODELS
class ReportBase(SQLModel):
    encrypted_blob: str = Field(description="Encrypted report content")
    channel_id: str = Field(description="Source channel/user ID for follow-up")
    source: ReportSource = Field(default=ReportSource.SLACK)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: IncidentStatus = Field(default=IncidentStatus.PENDING)
    severity: Optional[IncidentSeverity] = Field(default=None)
    categories: List[str] = Field(default=[], sa_column=Column(JSON))
    metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

class Report(ReportBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_by: Optional[str] = Field(default=None)
    review_notes: Optional[str] = Field(default=None)

class ReportCreate(ReportBase):
    pass

class ReportRead(ReportBase):
    id: int
    created_at: datetime
    updated_at: datetime
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None

class ReportUpdate(SQLModel):
    status: Optional[IncidentStatus] = None
    severity: Optional[IncidentSeverity] = None
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None

# ANALYTICS MODELS
class AnalyticsData(SQLModel):
    date: datetime
    incident_count: int
    category: str
    severity: Optional[str] = None

class IncidentTrend(BaseModel):
    date: str
    total_incidents: int
    by_severity: Dict[str, int]
    by_category: Dict[str, int]
    resolution_rate: float

class AnalyticsResponse(BaseModel):
    summary: Dict[str, Any]
    trends: List[IncidentTrend]
    categories: Dict[str, int]
    severity_distribution: Dict[str, int]

# DETECTION MODELS  
class DetectionRequest(BaseModel):
    text: str
    user_id: Optional[str] = None
    channel_type: Optional[str] = "public"

class DetectionResponse(BaseModel):
    flagged: bool
    confidence: float
    scores: Dict[str, float]
    categories: List[str]
    severity: str
    recommendations: List[str]

# ADMIN MODELS
class AdminUser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DashboardStats(BaseModel):
    total_reports: int
    pending_reports: int
    high_severity_reports: int
    reports_this_week: int
    resolution_rate: float
    top_categories: List[Dict[str, Any]]

# AUDIT LOG
class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    action: str = Field(index=True)
    user_id: Optional[str] = None
    report_id: Optional[int] = None
    details: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)

# SYSTEM CONFIG
class SystemConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True, index=True)
    value: str
    description: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
