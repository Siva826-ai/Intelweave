from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from app.db import models

def create_relationship(db: Session, case_id: UUID, source_id: UUID, target_id: UUID, 
                       basis: str, strength: float, confidence: float) -> models.Relationship:
    db_rel = models.Relationship(
        case_id=case_id,
        source_entity_id=source_id,
        target_entity_id=target_id,
        basis=basis,
        strength_score=strength,
        confidence_score=confidence,
        first_seen=datetime.utcnow(),
        last_seen=datetime.utcnow()
    )
    db.add(db_rel)
    db.commit()
    db.refresh(db_rel)
    return db_rel

def get_relationship_by_id(db: Session, rel_id: UUID) -> Optional[models.Relationship]:
    return db.get(models.Relationship, rel_id)

def get_relationships_by_case(db: Session, case_id: UUID) -> List[models.Relationship]:
    stmt = select(models.Relationship).where(models.Relationship.case_id == case_id)
    return list(db.scalars(stmt).all())

def get_relationships_by_entity(db: Session, entity_id: UUID) -> List[models.Relationship]:
    return db.query(models.Relationship).filter(
        (models.Relationship.source_entity_id == entity_id) | 
        (models.Relationship.target_entity_id == entity_id)
    ).all()

def count_relationships_by_case(db: Session, case_id: UUID) -> int:
    return db.query(models.Relationship).filter(models.Relationship.case_id == case_id).count()
