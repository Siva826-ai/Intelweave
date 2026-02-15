from fastapi import APIRouter, Depends, Query, Request
from uuid import UUID
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from app.db.schemas import EntityOut, EntityCreate, EvidenceOut, DataResponse, RelationshipOut
from typing import List
from app.services import entity_service
from app.api.deps import get_current_active_user
from app.services.audit_service import log_action

router = APIRouter()

@router.get("/search")
def search_entities(request: Request, q: str = Query(..., min_length=1), db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    log_action(db, user.user_id, "search_entities", "query", q, ip_address=request.client.host)
    rows = entity_service.search_entities(db, q)
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
def get_entity(entity_id: UUID, request: Request, db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    e = entity_service.get_entity(db, entity_id)
    if not e:
        return {"detail": "Not found"}
    log_action(db, user.user_id, "view_entity", "entity", str(entity_id), ip_address=request.client.host)
    return EntityOut(
        entity_id=e.entity_id, entity_type=e.entity_type, label=e.label,
        risk_score=float(e.risk_score), confidence_score=float(e.confidence_score)
    )

@router.get("/{entity_id}/timeline", response_model=DataResponse[List[EvidenceOut]])
def get_entity_timeline(entity_id: UUID, request: Request, db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    """
    Fetch the chronological timeline of events/evidence for a specific entity.
    """
    e = entity_service.get_entity(db, entity_id)
    if not e:
        return {"detail": "Entity not found"}
    
    timeline = entity_service.get_entity_timeline(db, entity_id)
    log_action(db, user.user_id, "view_entity_timeline", "entity", str(entity_id), ip_address=request.client.host)
    
    return {
        "data": timeline,
        "metadata": {
            "count": len(timeline),
            "entity_label": e.label
        }
    }

@router.get("/{entity_id}/connections", response_model=DataResponse[List[RelationshipOut]])
def get_entity_connections(entity_id: UUID, request: Request, db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    """
    Fetch all relationships associated with a specific entity (as either source or target).
    """
    e = entity_service.get_entity(db, entity_id)
    if not e:
        return {"detail": "Entity not found"}
    
    connections = entity_service.get_entity_connections(db, entity_id)
    log_action(db, user.user_id, "view_entity_connections", "entity", str(entity_id), ip_address=request.client.host)
    
    return {
        "data": connections,
        "metadata": {
            "count": len(connections),
            "entity_label": e.label
        }
    }
