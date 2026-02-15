from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from app.db import models
from typing import List, Optional

def get_user_by_id(db: Session, user_id: UUID) -> Optional[models.User]:
    return db.get(models.User, user_id)

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(func.lower(models.User.email) == email.lower()).first()

def create_user(db: Session, email: str, full_name: Optional[str] = None, clearance_level: int = 1) -> models.User:
    db_user = models.User(
        email=email.strip().lower(),
        full_name=full_name,
        clearance_level=clearance_level,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_all_users(db: Session, limit: int = 100) -> List[models.User]:
    return db.query(models.User).limit(limit).all()
