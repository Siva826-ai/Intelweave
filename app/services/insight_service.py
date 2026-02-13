from __future__ import annotations
from dataclasses import dataclass
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.db import models
from app.repositories import insight_repository

@dataclass
class InsightCard:
    severity: str
    summary: str
    explanation: str
    confidence_score: float
    basis: list[str]
    counter_evidence: list[str]

def generate_link_insight(strength_score: float, basis: list[str], gaps: list[str]) -> InsightCard:
    conf = min(100.0, max(0.0, strength_score))
    severity = "high" if conf >= 80 else "medium" if conf >= 60 else "low"
    summary = "Strong relationship pattern detected" if conf >= 70 else "Relationship pattern observed"
    explanation = (
        "Signal suggests repeated co-occurrence across sources. "
        "Confidence is derived from calibrated link-strength scoring."
    )
    return InsightCard(
        severity=severity,
        summary=summary,
        explanation=explanation,
        confidence_score=round(conf, 2),
        basis=basis,
        counter_evidence=gaps,
    )

def list_case_insights(db: Session, case_id: UUID, limit: int = 200) -> List[models.Insight]:
    return insight_repository.get_insights_by_case(db, case_id, limit)

def get_high_priority_signals(db: Session, limit: int = 50) -> List[models.Insight]:
    return insight_repository.get_high_priority_signals(db, limit)
