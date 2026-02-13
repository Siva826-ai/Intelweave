from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from app.db import models
from app.repositories import entity_repository, evidence_repository, relationship_repository

def get_entity(db: Session, entity_id: UUID) -> Optional[models.Entity]:
    return entity_repository.get_entity_by_id(db, entity_id)

def search_entities(db: Session, query: str, limit: int = 50) -> List[models.Entity]:
    return entity_repository.search_entities(db, query, limit)

def get_entity_timeline(db: Session, entity_id: UUID) -> List[models.EvidenceItem]:
    return evidence_repository.get_evidence_by_entity(db, entity_id)

def get_entity_connections(db: Session, entity_id: UUID) -> List[models.Relationship]:
    return relationship_repository.get_relationships_by_entity(db, entity_id)
