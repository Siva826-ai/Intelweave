from sqlalchemy.orm import Session
from uuid import UUID
from app.db import models
from typing import List, Optional

def get_insights_by_case(db: Session, case_id: UUID, limit: int = 200) -> List[models.Insight]:
    return db.query(models.Insight)\
        .filter(models.Insight.case_id == case_id)\
        .order_by(models.Insight.created_at.desc())\
        .limit(limit).all()

def get_high_priority_signals(db: Session, limit: int = 50) -> List[models.Insight]:
    return db.query(models.Insight).filter(
        models.Insight.severity.in_(["high", "critical"])
    ).order_by(models.Insight.created_at.desc()).limit(limit).all()

def count_insights_by_case(db: Session, case_id: UUID) -> int:
    return db.query(models.Insight).filter(models.Insight.case_id == case_id).count()
