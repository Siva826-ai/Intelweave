from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from app.db.schemas import CaseOut, CaseCreate
from app.core.security import require_clearance
from app.services import case_service
from app.api.deps import get_current_active_user

router = APIRouter()

_guard = require_clearance(1)


@router.post("/", response_model=CaseOut)
def create_case(payload: CaseCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_active_user)):
    return case_service.create_case(db, payload, user.user_id)


@router.get("/summary")
def cases_summary(db: Session = Depends(get_db), _=Depends(_guard)):
    # lightweight summary for dashboard
    total = db.query(models.Case).count()
    active = db.query(models.Case).filter(models.Case.status == "active").count()
    return {"total_cases": total, "active_cases": active}

@router.get("/{case_id}", response_model=CaseOut)
def get_case(case_id: UUID, db: Session = Depends(get_db), _=Depends(_guard)):
    c = db.get(models.Case, case_id)
    if not c:
        return {"detail": "Not found"}
    return CaseOut(
        case_id=c.case_id, title=c.title, status=c.status,
        jurisdiction=c.jurisdiction, integrity_score=float(c.integrity_score),
        created_at=c.created_at
    )

@router.get("/{case_id}/stats")
def case_stats(case_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    # 1. Entity Count
    entity_count = db.query(models.CaseEntity).filter(models.CaseEntity.case_id == case_id).count()
    
    # 2. Relationship Count
    rel_count = db.query(models.Relationship).filter(models.Relationship.case_id == case_id).count()
    
    # 3. Insight Count
    insight_count = db.query(models.Insight).filter(models.Insight.case_id == case_id).count()
    
    # 4. Evidence Count
    evidence_count = db.query(models.EvidenceItem).filter(models.EvidenceItem.case_id == case_id).count()
    
    return {
        "case_id": case_id,
        "stats": {
            "entities": entity_count,
            "relationships": rel_count,
            "insights": insight_count,
            "evidence": evidence_count
        }
    }

@router.get("/{case_id}/entities")
def get_case_entities(case_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    """
    List all entities involved in a specific case.
    """
    # Join CaseEntity and Entity to get details
    results = db.query(models.CaseEntity, models.Entity)\
        .join(models.Entity, models.CaseEntity.entity_id == models.Entity.entity_id)\
        .filter(models.CaseEntity.case_id == case_id)\
        .all()
    
    entities = []
    for case_entity, entity in results:
        entities.append({
            "entity_id": entity.entity_id,
            "label": entity.label,
            "type": entity.entity_type,
            "role": case_entity.role_in_case,
            "confidence": float(entity.confidence_score)
        })
        
    return {"case_id": case_id, "entities": entities}
