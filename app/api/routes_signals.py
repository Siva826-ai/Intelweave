from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.db import models
from app.db.schemas import InsightOut, DataResponse
from app.core.security import require_clearance

from app.core.security import require_clearance
from app.api.deps import get_current_active_user

router = APIRouter()

# _guard = require_clearance(1)

@router.get("/high-priority", response_model=DataResponse[List[InsightOut]])
def get_high_priority_signals(db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    """
    Fetch high-priority signals (Insights with severity 'high' or 'critical').
    """
    # Filter for high or critical severity
    signals = db.query(models.Insight).filter(
        models.Insight.severity.in_(["high", "critical"])
    ).order_by(models.Insight.created_at.desc()).limit(50).all()
    
    return {
        "data": signals,
        "metadata": {
            "count": len(signals),
            "description": "High priority insights requiring attention"
        }
    }
