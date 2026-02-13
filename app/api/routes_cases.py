from fastapi import APIRouter, Depends, Query, Request
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from app.db.schemas import CaseOut, CaseCreate, CaseGraph, EvidenceOut
from typing import List, Optional
from app.core.security import require_clearance
from app.services import case_service, audit_service, insight_service
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
    return case_service.get_cases_summary(db)

@router.get("/{case_id}", response_model=CaseOut)
def get_case(case_id: UUID, db: Session = Depends(get_db), _=Depends(_guard)):
    c = case_service.get_case(db, case_id)
    if not c:
        return {"detail": "Not found"}
    return c

@router.get("/{case_id}/stats")
def case_stats(case_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    stats = case_service.get_case_stats(db, case_id)
    return {
        "case_id": case_id,
        "stats": stats
    }

@router.get("/{case_id}/entities")
def get_case_entities(case_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    entities = case_service.get_case_entities(db, case_id)
    return {"case_id": case_id, "entities": entities}

@router.get("/{case_id}/graph", response_model=CaseGraph)
def get_case_graph(case_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    return case_service.get_case_graph(db, case_id)

@router.get("/{case_id}/timeline", response_model=List[EvidenceOut])
def get_case_timeline(
    case_id: UUID, 
    range: Optional[str] = Query(None),
    db: Session = Depends(get_db), 
    user=Depends(get_current_active_user)
):
    return case_service.get_case_timeline(db, case_id, range)

@router.get("/{case_id}/integrity-hash")
def get_case_integrity_hash(case_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    result = case_service.get_case_integrity_hash(db, case_id)
    if not result:
        return {"detail": "Not found"}
    
    return {
        "case_id": case_id,
        **result
    }

@router.get("/{case_id}/insights")
def list_case_insights(case_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    """
    List all insights associated with a specific case.
    """
    rows = insight_service.list_case_insights(db, case_id)
    return {"case_id": case_id, "items": [
        {
            "insight_id": str(r.insight_id),
            "severity": r.severity,
            "summary": r.summary,
            "confidence_score": float(r.confidence_score),
            "created_at": r.created_at.isoformat()
        } for r in rows
    ]}
