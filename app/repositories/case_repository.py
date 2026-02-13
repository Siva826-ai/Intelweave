from sqlalchemy.orm import Session
from uuid import UUID
from app.db import models
from typing import List, Optional

def get_case_by_id(db: Session, case_id: UUID) -> Optional[models.Case]:
    return db.get(models.Case, case_id)

def get_all_cases(db: Session, limit: int = 100) -> List[models.Case]:
    return db.query(models.Case).limit(limit).all()

def count_total_cases(db: Session) -> int:
    return db.query(models.Case).count()

def count_active_cases(db: Session) -> int:
    return db.query(models.Case).filter(models.Case.status == "active").count()

def create_case(db: Session, title: str, status: str, jurisdiction: str) -> models.Case:
    db_case = models.Case(
        title=title,
        status=status,
        jurisdiction=jurisdiction,
        created_by=None
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case
