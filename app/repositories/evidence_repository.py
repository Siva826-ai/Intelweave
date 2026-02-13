from sqlalchemy.orm import Session
from uuid import UUID
from app.db import models
from typing import List, Optional
from datetime import datetime

def create_evidence(db: Session, case_id: UUID, insight_id: Optional[UUID], entity_id: Optional[UUID], 
                    rel_id: Optional[UUID], evidence_type: str, description: str, evidence_hash: str) -> models.EvidenceItem:
    db_evidence = models.EvidenceItem(
        case_id=case_id,
        insight_id=insight_id,
        entity_id=entity_id,
        rel_id=rel_id,
        evidence_type=evidence_type,
        description=description,
        evidence_hash=evidence_hash
    )
    db.add(db_evidence)
    db.commit()
    db.refresh(db_evidence)
    return db_evidence

def get_evidence_by_case(db: Session, case_id: UUID, since: Optional[datetime] = None) -> List[models.EvidenceItem]:
    query = db.query(models.EvidenceItem).filter(models.EvidenceItem.case_id == case_id)
    if since:
        query = query.filter(models.EvidenceItem.created_at >= since)
    return query.order_by(models.EvidenceItem.created_at.asc()).all()

def get_evidence_by_entity(db: Session, entity_id: UUID) -> List[models.EvidenceItem]:
    return db.query(models.EvidenceItem)\
        .filter(models.EvidenceItem.entity_id == entity_id)\
        .order_by(models.EvidenceItem.created_at.asc())\
        .all()

def count_evidence_by_case(db: Session, case_id: UUID) -> int:
    return db.query(models.EvidenceItem).filter(models.EvidenceItem.case_id == case_id).count()
