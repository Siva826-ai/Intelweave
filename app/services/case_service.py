from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from typing import List, Optional
import hashlib

from app.db import models
from app.db.schemas import CaseCreate
from app.repositories import case_repository, entity_repository, evidence_repository, insight_repository, relationship_repository

def create_case(db: Session, payload: CaseCreate, user_id: UUID) -> models.Case:
    return case_repository.create_case(db, payload.title, payload.status, payload.jurisdiction)

def get_case(db: Session, case_id: UUID) -> models.Case | None:
    return case_repository.get_case_by_id(db, case_id)

def get_cases_summary(db: Session) -> dict:
    return {
        "total_cases": case_repository.count_total_cases(db),
        "active_cases": case_repository.count_active_cases(db)
    }

def get_case_stats(db: Session, case_id: UUID) -> dict:
    return {
        "entities": entity_repository.get_entities_by_case(db, case_id), # This returns objects, counts needed
        "relationships": relationship_repository.count_relationships_by_case(db, case_id),
        "insights": insight_repository.count_insights_by_case(db, case_id),
        "evidence": evidence_repository.count_evidence_by_case(db, case_id)
    }

# Correction: stats needs counts, not objects.
def get_case_stats(db: Session, case_id: UUID) -> dict:
    # Need to add count method to EntityRepo or use existing ones
    # For now I will use what I have or fix repositories if needed.
    # Actually, I'll just use the specific counts.
    entities_count = len(entity_repository.get_entities_by_case(db, case_id))
    return {
        "entities": entities_count,
        "relationships": relationship_repository.count_relationships_by_case(db, case_id),
        "insights": insight_repository.count_insights_by_case(db, case_id),
        "evidence": evidence_repository.count_evidence_by_case(db, case_id)
    }

def get_case_entities(db: Session, case_id: UUID) -> List[dict]:
    results = entity_repository.get_entities_by_case(db, case_id)
    entities = []
    for case_entity, entity in results:
        entities.append({
            "entity_id": entity.entity_id,
            "label": entity.label,
            "type": entity.entity_type,
            "role": case_entity.role_in_case,
            "confidence": float(entity.confidence_score)
        })
    return entities

def get_case_graph(db: Session, case_id: UUID) -> dict:
    entities = entity_repository.get_entities_by_case_raw(db, case_id)
    relationships = relationship_repository.get_relationships_by_case(db, case_id)
    
    nodes = [{"id": e.entity_id, "label": e.label, "type": e.entity_type} for e in entities]
    edges = [
        {
            "id": r.rel_id, 
            "source": r.source_entity_id, 
            "target": r.target_entity_id, 
            "basis": r.basis,
            "weight": float(r.strength_score)
        } for r in relationships
    ]
    return {"nodes": nodes, "edges": edges}

def get_case_timeline(db: Session, case_id: UUID, time_range: Optional[str] = None) -> List[models.EvidenceItem]:
    since = None
    if time_range:
        import re
        from datetime import timedelta
        match = re.match(r"(\d+)d", time_range)
        if match:
            days = int(match.group(1))
            since = datetime.utcnow() - timedelta(days=days)

    return evidence_repository.get_evidence_by_case(db, case_id, since=since)

def get_case_integrity_hash(db: Session, case_id: UUID) -> Optional[dict]:
    c = case_repository.get_case_by_id(db, case_id)
    if not c:
        return None
        
    raw_str = f"{c.case_id}:{c.title}:{c.integrity_score}"
    h = hashlib.sha256(raw_str.encode()).hexdigest()
    
    return {
        "integrity_hash": h,
        "algorithm": "sha256",
        "timestamp": c.created_at.isoformat()
    }
