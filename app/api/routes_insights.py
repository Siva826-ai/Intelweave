from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from app.core.security import require_clearance

router = APIRouter()

_guard = require_clearance(1)


@router.get("/case/{case_id}")
def list_case_insights(case_id: str, db: Session = Depends(get_db), _=Depends(_guard)):
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

@router.post("/hypothesis")
def create_hypothesis(payload: dict, db: Session = Depends(get_db), _=Depends(_guard)):
    # Stub: you will validate payload and run AI scoring here.
    return {"status": "received", "payload": payload, "note": "Wire to AI hypothesis pipeline."}
