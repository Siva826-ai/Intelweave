from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from app.db import models
from app.db.schemas import RelationshipCreate
from app.services.audit_service import log_action
from app.repositories import relationship_repository

def create_relationship(db: Session, case_id: UUID, relationship: RelationshipCreate, user_id: UUID) -> models.Relationship:
    db_rel = relationship_repository.create_relationship(
        db, 
        case_id=case_id,
        source_id=relationship.source_entity_id,
        target_id=relationship.target_entity_id,
        basis=relationship.basis,
        strength=relationship.strength_score,
        confidence=relationship.confidence_score
    )
    
    log_action(db, user_id, "create", "relationship", str(db_rel.rel_id), case_id)
    return db_rel

def get_relationships(db: Session, case_id: UUID) -> List[models.Relationship]:
    return relationship_repository.get_relationships_by_case(db, case_id)

def get_relationship(db: Session, rel_id: UUID) -> Optional[models.Relationship]:
    return relationship_repository.get_relationship_by_id(db, rel_id)
