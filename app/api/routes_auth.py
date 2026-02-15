from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.db import models
from app.db.schemas import UserCreate, UserOut, DataResponse
from app.core import security
from app.api.deps import get_current_active_user
from app.services import user_service
from uuid import UUID

router = APIRouter()

@router.post("/login")
def login(email: str = Body(..., embed=True), db: Session = Depends(get_db)):
    """
    Temporary login for development. In production, this would use passwords or SSO.
    """
    email = email.strip().lower()
    user = db.query(models.User).filter(func.lower(models.User.email) == email).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{email}' not found. Please use 'admin@intelweave.local' or your registered email.")
    
    token_data = {
        "sub": str(user.user_id),
        "email": user.email,
        "clearance_level": user.clearance_level,
        "roles": [] # Add roles if available in model later
    }
    
    access_token = security.create_access_token(token_data)
    refresh_token = security.create_refresh_token(token_data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
def refresh_token(refresh_token: str = Body(..., embed=True)):
    """
    Exchange a refresh token for a new access token.
    """
    payload = security.decode_token(refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    
    # Create new access token from payload
    token_data = {
        "sub": payload.get("sub"),
        "email": payload.get("email"),
        "clearance_level": payload.get("clearance_level"),
        "roles": payload.get("roles")
    }
    
    new_access_token = security.create_access_token(token_data)
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@router.post("/register", response_model=DataResponse[UserOut])
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    existing_user = user_service.get_user_by_email(db, payload.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = user_service.create_user(db, payload)
    return {
        "data": user,
        "metadata": {
            "timestamp": user.created_at.isoformat()
        }
    }

@router.get("/me")
def get_me(user: models.User = Depends(get_current_active_user)):
    return user