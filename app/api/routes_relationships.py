from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from datetime import datetime

from app.db.session import get_db
from app.db.schemas import RelationshipCreate, RelationshipOut, DataResponse
from app.api.deps import get_current_active_user
from app.db import models
from app.services import relationship_service

router = APIRouter()

@router.post("/{case_id}/relationships", response_model=DataResponse[RelationshipOut])
def create_relationship_endpoint(
    case_id: UUID,
    payload: RelationshipCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_active_user)
):
    # Relies on service to check existence
    rel = relationship_service.create_relationship(db, case_id, payload, user.user_id)
    return {
        "data": rel,
        "metadata": {
            "case_id": str(case_id),
            "timestamp": rel.created_at.isoformat()
        }
    }

@router.get("/{case_id}/relationships", response_model=DataResponse[List[RelationshipOut]])
def get_relationships_endpoint(
    case_id: UUID,
    db: Session = Depends(get_db)
):
    rels = relationship_service.get_relationships(db, case_id)
    return {
        "data": rels,
        "metadata": {
            "case_id": str(case_id),
            "timestamp": datetime.utcnow().isoformat()
        }
    }

@router.get("/{rel_id}", response_model=DataResponse[RelationshipOut])
def get_relationship_endpoint(
    rel_id: UUID,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_active_user)
):
    """
    Retrieves a single relationship by its ID.
    """
    rel = relationship_service.get_relationship(db, rel_id)
    if not rel:
        raise HTTPException(status_code=404, detail="Relationship not found")
    
    return {
        "data": rel,
        "metadata": {
            "rel_id": str(rel_id),
            "timestamp": datetime.utcnow().isoformat()
        }
    }
