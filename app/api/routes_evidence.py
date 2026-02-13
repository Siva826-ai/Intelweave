from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.db.session import get_db
from app.db.schemas import EvidenceCreate, EvidenceOut, DataResponse
from typing import List
from app.services import evidence_service
from app.api.deps import get_current_active_user
from app.db import models
from app.services.audit_service import log_action

router = APIRouter()

@router.post("/{case_id}/evidence", response_model=DataResponse[EvidenceOut])
def create_evidence_endpoint(
    case_id: UUID,
    payload: EvidenceCreate,
    request: Request,
    db: Session = Depends(get_db),
    court_mode: bool = Query(False),
    user: models.User = Depends(get_current_active_user)
):
    if court_mode:
        raise HTTPException(status_code=403, detail="Modifications forbidden in Court Mode")
        
    evidence = evidence_service.create_evidence(db, case_id, payload, user.user_id)
    log_action(db, user.user_id, "create_evidence", "evidence", str(evidence.evidence_id), case_id, request.client.host)
    return {
        "data": evidence,
        "metadata": {
            "case_id": str(case_id),
            "timestamp": evidence.created_at.isoformat()
        }
    }

@router.get("/{case_id}/evidence", response_model=DataResponse[List[EvidenceOut]])
def list_case_evidence_endpoint(
    case_id: UUID,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_active_user)
):
    """
    Lists all evidence items associated with a specific case.
    """
    items = evidence_service.get_case_evidence(db, case_id)
    return {
        "data": items,
        "metadata": {
            "case_id": str(case_id),
            "count": len(items)
        }
    }
