from app.db.session import SessionLocal
from app.db import models
import uuid
from datetime import datetime

def seed():
    db = SessionLocal()
    case_id = uuid.UUID('f4952490-64a6-4c6c-a727-f0c68f38d500')
    john_id = uuid.UUID('9e47e4b5-9e99-4992-8a25-97d44b1a8622')
    
    # 1. Jane
    jane_id = uuid.uuid4()
    jane = models.Entity(entity_id=jane_id, label="Jane Smith", entity_type="person")
    db.add(jane)
    try:
        db.commit()
    except:
        db.rollback()
        # Assume exists or other error, try to fetch or just continue
        jane_existent = db.query(models.Entity).filter(models.Entity.label == "Jane Smith").first()
        if jane_existent: jane_id = jane_existent.entity_id

    # 2. Relationship
    rel_id = uuid.uuid4()
    rel = models.Relationship(
        rel_id=rel_id,
        case_id=case_id,
        source_entity_id=john_id,
        target_entity_id=jane_id,
        basis="manual_observation",
        strength_score=80.0,
        confidence_score=90.0
    )
    db.add(rel)
    try:
        db.commit()
        print(f"SUCCESS|REL_ID:{rel_id}")
    except Exception as e:
        print(f"FAILURE|{e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
