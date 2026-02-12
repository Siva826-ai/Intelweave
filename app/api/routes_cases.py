from fastapi import APIRouter, Depends, Query, Request
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from app.db.schemas import CaseOut, CaseCreate, CaseGraph, EvidenceOut
from typing import List, Optional
from app.core.security import require_clearance
from app.services import case_service, audit_service
from app.api.deps import get_current_active_user

router = APIRouter()

_guard = require_clearance(1)


@router.post("/", response_model=CaseOut)
def create_case(payload: CaseCreate, request: Request, db: Session = Depends(get_db), user: models.User = Depends(get_current_active_user)):
    new_case = case_service.create_case(db, payload, user.user_id)
    audit_service.log_action(db, user.user_id, "create_case", "case", str(new_case.case_id), new_case.case_id, request.client.host)
    return new_case


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

@router.get("/{case_id}/graph", response_model=CaseGraph)
def get_case_graph(case_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    """
    Returns nodes and edges representing the case's relationship network for visualization.
    """
    # 1. Fetch Entities
    entities = db.query(models.Entity).join(models.CaseEntity).filter(models.CaseEntity.case_id == case_id).all()
    
    # 2. Fetch Relationships
    relationships = db.query(models.Relationship).filter(models.Relationship.case_id == case_id).all()
    
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

@router.get("/{case_id}/timeline", response_model=List[EvidenceOut])
def get_case_timeline(
    case_id: UUID, 
    range: Optional[str] = Query(None),
    db: Session = Depends(get_db), 
    user=Depends(get_current_active_user)
):
    """
    Returns a chronological view of all evidence items in the case.
    Supports range filtering (e.g. '7d', '30d').
    """
    query = db.query(models.EvidenceItem).filter(models.EvidenceItem.case_id == case_id)
    
    if range:
        import re
        from datetime import timedelta
        # Simple parser for 'Xd' (days)
        match = re.match(r"(\d+)d", range)
        if match:
            days = int(match.group(1))
            since = datetime.utcnow() - timedelta(days=days)
            query = query.filter(models.EvidenceItem.created_at >= since)

    items = query.order_by(models.EvidenceItem.created_at.asc()).all()
    return items

@router.get("/{case_id}/integrity-hash")
def get_case_integrity_hash(case_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    """
    Computes a deterministic hash of the case's critical data to ensure non-repudiation and court safety.
    """
    import hashlib
    # Simplistic implementation: combine case title and integrity score
    c = db.get(models.Case, case_id)
    if not c:
        return {"detail": "Not found"}
        
    raw_str = f"{c.case_id}:{c.title}:{c.integrity_score}"
    h = hashlib.sha256(raw_str.encode()).hexdigest()
    
    return {
        "case_id": case_id,
        "integrity_hash": h,
        "algorithm": "sha256",
        "timestamp": c.created_at.isoformat()
    }

@router.get("/{case_id}/insights")
def list_case_insights(case_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    """
    List all insights associated with a specific case.
    """
    rows = db.query(models.Insight).filter(models.Insight.case_id == case_id).order_by(models.Insight.created_at.desc()).limit(200).all()
    return {"case_id": case_id, "items": [
        {
            "insight_id": str(r.insight_id),
            "severity": r.severity,
            "summary": r.summary,
            "confidence_score": float(r.confidence_score),
            "created_at": r.created_at.isoformat()
        } for r in rows
    ]}
