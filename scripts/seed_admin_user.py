import uuid
from datetime import datetime
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import SessionLocal
from app.db import models

def seed_admin():
    db = SessionLocal()
    try:
        email = "admin@intelweave.local"
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            user = models.User(
                user_id=uuid.uuid4(),
                email=email,
                full_name="System Admin",
                clearance_level=5,
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(user)
            db.commit()
            print(f"SUCCESS: Created user {email}")
        else:
            print(f"INFO: User {email} already exists")
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()
