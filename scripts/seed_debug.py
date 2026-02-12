from app.db.session import SessionLocal
from app.db import models
import uuid
from datetime import datetime
import traceback

def seed():
    db = SessionLocal()
    try:
        eid = uuid.uuid4()
        entity = models.Entity(
            entity_id=eid,
            label="John Doe",
            entity_type="person",
            risk_score=0.0,
            confidence_score=0.0
        )
        db.add(entity)
        db.commit()
        print(f"SUCCESS|{eid}")
    except Exception:
        print("FAILURE")
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
