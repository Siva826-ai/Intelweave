from fastapi import Depends
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.routes_cases import get_db # Initially import get_db from where available or session
# Better to import get_db from app.db.session
from app.db.session import get_db
from app.db import models
from app.core.security import require_clearance, CurrentUser

# Re-export get_db for convenience
# (already imported)

def get_current_active_user(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_clearance(1))
) -> models.User:
    """
    Get the current user from the token.
    If the user does not exist in the DB, create them (JIT provisioning).
    """
    user_id = UUID(current_user.user_id)
    user = db.get(models.User, user_id)
    
    if not user:
        # JIT Provisioning
        email = current_user.email or f"user_{user_id}@intelweave.local"
        
        # Check if email is already taken by another user
        if db.query(models.User).filter(models.User.email == email).first():
            # Fallback to unique email if collision
            email = f"user_{user_id}@intelweave.local"

        user = models.User(
            user_id=user_id,
            email=email,
            full_name="JIT Provisioned User",
            clearance_level=current_user.clearance_level,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
    return user
