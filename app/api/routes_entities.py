from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from app.db.schemas import EntityOut
from app.core.security import require_clearance

router = APIRouter()

_guard = require_clearance(1)


@router.get("/search")
def search_entities(q: str = Query(..., min_length=1), db: Session = Depends(get_db), _=Depends(_guard)):
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
def get_entity(entity_id: str, db: Session = Depends(get_db), _=Depends(_guard)):
    e = db.get(models.Entity, entity_id)
    if not e:
        return {"detail": "Not found"}
    return EntityOut(
        entity_id=e.entity_id, entity_type=e.entity_type, label=e.label,
        risk_score=float(e.risk_score), confidence_score=float(e.confidence_score)
    )
