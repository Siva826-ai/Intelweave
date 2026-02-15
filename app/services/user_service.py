from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from app.db import models
from app.db.schemas import UserCreate
from app.repositories import user_repository

def get_user(db: Session, user_id: UUID) -> Optional[models.User]:
    return user_repository.get_user_by_id(db, user_id)

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return user_repository.get_user_by_email(db, email)

def create_user(db: Session, payload: UserCreate) -> models.User:
    return user_repository.create_user(
        db,
        email=payload.email,
        full_name=payload.full_name,
        clearance_level=payload.clearance_level
    )

def list_users(db: Session, limit: int = 100) -> List[models.User]:
    return user_repository.get_all_users(db, limit)
