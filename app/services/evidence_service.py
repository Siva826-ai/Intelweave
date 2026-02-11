import hashlib
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.models import EvidenceItem
from app.db.schemas import EvidenceCreate
from app.services.audit_service import log_action

def create_evidence(db: Session, case_id: UUID, evidence: EvidenceCreate, user_id: UUID) -> EvidenceItem:
    # Generate Hash
    hash_input = f"{case_id}{evidence.evidence_type}{evidence.description}".encode()
    evidence_hash = hashlib.sha256(hash_input).hexdigest()
    
    db_evidence = EvidenceItem(
        case_id=case_id,
        insight_id=evidence.insight_id,
        entity_id=evidence.entity_id,
        rel_id=evidence.rel_id,
        evidence_type=evidence.evidence_type,
        description=evidence.description,
        evidence_hash=evidence_hash
    )
    db.add(db_evidence)
    db.commit()
    db.refresh(db_evidence)
    
    log_action(db, user_id, "create", "evidence", str(db_evidence.evidence_id), case_id)
    return db_evidence
