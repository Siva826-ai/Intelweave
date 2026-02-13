from sqlalchemy.orm import Session
from uuid import UUID
from app.db import models
from typing import List, Optional

def get_entity_by_id(db: Session, entity_id: UUID) -> Optional[models.Entity]:
    return db.get(models.Entity, entity_id)

def search_entities(db: Session, query: str, limit: int = 50) -> List[models.Entity]:
    return db.query(models.Entity).filter(models.Entity.label.ilike(f"%{query}%")).limit(limit).all()

def get_entities_by_case(db: Session, case_id: UUID) -> List[tuple[models.CaseEntity, models.Entity]]:
    return db.query(models.CaseEntity, models.Entity)\
        .join(models.Entity, models.CaseEntity.entity_id == models.Entity.entity_id)\
        .filter(models.CaseEntity.case_id == case_id)\
        .all()

def get_entities_by_case_raw(db: Session, case_id: UUID) -> List[models.Entity]:
    return db.query(models.Entity).join(models.CaseEntity).filter(models.CaseEntity.case_id == case_id).all()
