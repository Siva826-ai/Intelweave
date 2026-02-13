from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.db import models
from app.db.schemas import InsightOut, DataResponse
from app.services import insight_service
from app.api.deps import get_current_active_user

router = APIRouter()

@router.get("/high-priority", response_model=DataResponse[List[InsightOut]])
def get_high_priority_signals(db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    """
    Fetch high-priority signals (Insights with severity 'high' or 'critical').
    """
    signals = insight_service.get_high_priority_signals(db)
    
    return {
        "data": signals,
        "metadata": {
            "count": len(signals),
            "description": "High priority insights requiring attention"
        }
    }
