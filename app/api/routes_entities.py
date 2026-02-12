from fastapi import APIRouter, Depends, Query, Request
from uuid import UUID
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from app.db.schemas import EntityOut, EvidenceOut, DataResponse, RelationshipOut
from typing import List
from app.core.security import require_clearance
from app.api.deps import get_current_active_user
from app.services.audit_service import log_action

router = APIRouter()

# _guard = require_clearance(1) - Removed global guard to use per-route dependency if needed, or just replace usage


@router.get("/search")
def search_entities(request: Request, q: str = Query(..., min_length=1), db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    log_action(db, user.user_id, "search_entities", "query", q, ip_address=request.client.host)
    rows = db.query(models.Entity).filter(models.Entity.label.ilike(f"%{q}%")).limit(50).all()
    return {
        "query": q,
        "results": [
            EntityOut(
                entity_id=r.entity_id, entity_type=r.entity_type, label=r.label,
                risk_score=float(r.risk_score), confidence_score=float(r.confidence_score)
            ).model_dump()
            for r in rows
        ]
    }

@router.get("/{entity_id}")
def get_entity(entity_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    e = db.get(models.Entity, entity_id)
    if not e:
        return {"detail": "Not found"}
    return EntityOut(
        entity_id=e.entity_id, entity_type=e.entity_type, label=e.label,
        risk_score=float(e.risk_score), confidence_score=float(e.confidence_score)
    )

@router.get("/{entity_id}/timeline", response_model=DataResponse[List[EvidenceOut]])
def get_entity_timeline(entity_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    """
    Fetch the chronological timeline of events/evidence for a specific entity.
    """
    # 1. Verify entity exists
    e = db.get(models.Entity, entity_id)
    if not e:
        return {"detail": "Entity not found"}
    
    # 2. Fetch evidence items linked to this entity, sorted by creation date
    timeline = db.query(models.EvidenceItem)\
        .filter(models.EvidenceItem.entity_id == entity_id)\
        .order_by(models.EvidenceItem.created_at.asc())\
        .all()
    
    return {
        "data": timeline,
        "metadata": {
            "count": len(timeline),
            "entity_label": e.label
        }
    }

@router.get("/{entity_id}/connections", response_model=DataResponse[List[RelationshipOut]])
def get_entity_connections(entity_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    """
    Fetch all relationships associated with a specific entity (as either source or target).
    """
    # 1. Verify entity exists
    e = db.get(models.Entity, entity_id)
    if not e:
        return {"detail": "Entity not found"}
    
    # 2. Query relationships where entity is source OR target
    connections = db.query(models.Relationship).filter(
        (models.Relationship.source_entity_id == entity_id) | 
        (models.Relationship.target_entity_id == entity_id)
    ).all()
    
    return {
        "data": connections,
        "metadata": {
            "count": len(connections),
            "entity_label": e.label
        }
    }
