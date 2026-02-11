from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from datetime import datetime

from app.api.deps import get_db
from app.db.schemas import RelationshipCreate, RelationshipOut, DataResponse
from app.services import relationship_service

router = APIRouter()

@router.post("/{case_id}/relationships", response_model=DataResponse[RelationshipOut])
def create_relationship_endpoint(
    case_id: UUID,
    payload: RelationshipCreate,
    db: Session = Depends(get_db),
    # In a real app, we'd get user_id from auth token. Using a placeholder or header for now.
    user_id: UUID = UUID("00000000-0000-0000-0000-000000000000") 
):
    # TODO: Validate case_id exists
    rel = relationship_service.create_relationship(db, case_id, payload, user_id)
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
