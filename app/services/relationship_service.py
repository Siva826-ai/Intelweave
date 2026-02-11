from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from datetime import datetime
from app.db.models import Relationship
from app.db.schemas import RelationshipCreate
from app.services.audit_service import log_action

def create_relationship(db: Session, case_id: UUID, relationship: RelationshipCreate, user_id: UUID) -> Relationship:
    db_rel = Relationship(
        case_id=case_id,
        source_entity_id=relationship.source_entity_id,
        target_entity_id=relationship.target_entity_id,
        basis=relationship.basis,
        strength_score=relationship.strength_score,
        confidence_score=relationship.confidence_score,
        first_seen=datetime.utcnow(),
        last_seen=datetime.utcnow()
    )
    db.add(db_rel)
    db.commit()
    db.refresh(db_rel)
    
    log_action(db, user_id, "create", "relationship", str(db_rel.rel_id), case_id)
    return db_rel

def get_relationships(db: Session, case_id: UUID) -> list[Relationship]:
    stmt = select(Relationship).where(Relationship.case_id == case_id)
    return db.scalars(stmt).all()
