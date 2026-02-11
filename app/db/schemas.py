from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class CaseOut(BaseModel):
    case_id: UUID
    title: str
    status: str
    jurisdiction: Optional[str] = None
    integrity_score: float = Field(ge=0, le=100)
    created_at: datetime

class EntityOut(BaseModel):
    entity_id: UUID
    entity_type: str
    label: str
    risk_score: float = Field(ge=0, le=100)
    confidence_score: float = Field(ge=0, le=100)

class InsightOut(BaseModel):
    insight_id: UUID
    case_id: UUID
    severity: str
    summary: str
    explanation: Optional[str] = None
    confidence_score: float = Field(ge=0, le=100)
    created_at: datetime
