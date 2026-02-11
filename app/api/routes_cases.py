from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from app.db.schemas import CaseOut
from app.core.security import require_clearance

router = APIRouter()

_guard = require_clearance(1)


@router.get("/summary")
def cases_summary(db: Session = Depends(get_db), _=Depends(_guard)):
    # lightweight summary for dashboard
    total = db.query(models.Case).count()
    active = db.query(models.Case).filter(models.Case.status == "active").count()
    return {"total_cases": total, "active_cases": active}

@router.get("/{case_id}", response_model=CaseOut)
def get_case(case_id: str, db: Session = Depends(get_db), _=Depends(_guard)):
    c = db.get(models.Case, case_id)
    if not c:
        return {"detail": "Not found"}
    return CaseOut(
        case_id=c.case_id, title=c.title, status=c.status,
        jurisdiction=c.jurisdiction, integrity_score=float(c.integrity_score),
        created_at=c.created_at
    )

@router.get("/{case_id}/stats")
def case_stats(case_id: str, db: Session = Depends(get_db), _=Depends(_guard)):
    # stub: extend with entities/relationships/insights counts
    return {"case_id": case_id, "note": "Implement entity/relationship counters here."}
