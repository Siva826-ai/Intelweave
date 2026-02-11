from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.db.session import get_db
from app.db.schemas import EvidenceCreate, EvidenceOut, DataResponse
from app.services import evidence_service

router = APIRouter()

@router.post("/{case_id}/evidence", response_model=DataResponse[EvidenceOut])
def create_evidence_endpoint(
    case_id: UUID,
    payload: EvidenceCreate,
    db: Session = Depends(get_db),
    court_mode: bool = Query(False),
    user_id: UUID = UUID("00000000-0000-0000-0000-000000000000")
):
    if court_mode:
        raise HTTPException(status_code=403, detail="Modifications forbidden in Court Mode")
        
    evidence = evidence_service.create_evidence(db, case_id, payload, user_id)
    return {
        "data": evidence,
        "metadata": {
            "case_id": str(case_id),
            "timestamp": evidence.created_at.isoformat()
        }
    }
