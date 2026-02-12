from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.db import models
from app.core.security import require_clearance
from app.api.deps import get_current_active_user

router = APIRouter()

# _guard = require_clearance(1)

@router.get("/integrity")
def get_system_integrity(db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    """
    Get system-wide integrity metrics.
    """
    # 1. Database Connectivity (Implicit by getting here)
    
    # 2. Key Metrics
    total_cases = db.query(models.Case).count()
    active_cases = db.query(models.Case).filter(models.Case.status == "active").count()
    
    # 3. Calculate Average Integrity Score (if cases exist)
    avg_integrity = db.query(func.avg(models.Case.integrity_score)).scalar() or 100.0
    
    # 4. System Status Logic (Placeholder)
    system_status = "operational"
    if float(avg_integrity) < 50.0:
        system_status = "degraded"
        
    return {
        "status": system_status,
        "metrics": {
            "total_cases": total_cases,
            "active_cases": active_cases,
            "system_integrity_score": float(avg_integrity),
            "database_connected": True
        },
        "version": "1.0.0"
    }
