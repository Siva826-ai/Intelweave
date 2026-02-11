from __future__ import annotations
from dataclasses import dataclass

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
