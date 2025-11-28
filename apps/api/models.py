from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class ReportBase(SQLModel):
    encrypted_blob: str
    channel_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="pending") # pending, reviewed, resolved

class Report(ReportBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class ReportCreate(ReportBase):
    pass

class ReportRead(ReportBase):
    id: int

class AnalyticsData(SQLModel):
    date: datetime
    incident_count: int
    category: str
