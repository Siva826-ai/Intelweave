from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Generic, TypeVar, Any, List
from uuid import UUID
from datetime import datetime

T = TypeVar("T")

class DataResponse(BaseModel, Generic[T]):
    data: T
    metadata: dict[str, Any]

class RelationshipCreate(BaseModel):
    source_entity_id: UUID
    target_entity_id: UUID
    basis: str
    strength_score: float = Field(ge=0, le=100)
    confidence_score: float = Field(ge=0, le=100)

class RelationshipOut(RelationshipCreate):
    rel_id: UUID
    case_id: UUID
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class EvidenceCreate(BaseModel):
    insight_id: Optional[UUID] = None
    entity_id: Optional[UUID] = None
    rel_id: Optional[UUID] = None
    evidence_type: str
    description: str

class EvidenceOut(EvidenceCreate):
    evidence_id: UUID
    case_id: UUID
    evidence_hash: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ExportCreate(BaseModel):
    export_type: str

class ExportOut(BaseModel):
    export_id: UUID
    case_id: UUID
    export_type: str
    requested_by: UUID
    export_hash: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AuditLogOut(BaseModel):
    log_id: UUID
    user_id: UUID
    case_id: Optional[UUID] = None
    action: str
    target_type: str
    target_id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class IngestJobCreate(BaseModel):
    source_type: str

class IngestJobOut(BaseModel):
    job_id: UUID
    case_id: UUID
    source_type: str
    validation_score: float
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class IngestFileOut(BaseModel):
    file_id: UUID
    job_id: UUID
    filename: str
    file_type: str
    sha256_hash: str
    row_count: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)




class CaseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    jurisdiction: Optional[str] = None
    status: str = "draft"

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
