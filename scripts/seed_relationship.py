from app.db.session import SessionLocal
from app.db import models
import uuid
from datetime import datetime

def seed_relationship():
    db = SessionLocal()
    try:
        case_id = uuid.UUID('f4952490-64a6-4c6c-a727-f0c68f38d500') # Operation Nightfall
        john_id = uuid.UUID('9e47e4b5-9e99-4992-8a25-97d44b1a8622')
        
        # 1. Create Jane Smith
        jane_id = uuid.uuid4()
        jane = models.Entity(
            entity_id=jane_id,
            label="Jane Smith",
            entity_type="person",
            risk_score=20.0,
            confidence_score=85.0,
            created_at=datetime.utcnow()
        )
        db.add(jane)
        
        # 2. Link Jane to Case
        ce = models.CaseEntity(
            case_id=case_id,
            entity_id=jane_id,
            role_in_case="associate"
        )
        db.add(ce)
        
        # 3. Create Relationship (John -> Jane)
        rel_id = uuid.uuid4()
        rel = models.Relationship(
            rel_id=rel_id,
            case_id=case_id,
            source_entity_id=john_id,
            target_entity_id=jane_id,
            basis="frequent_calls",
            strength_score=75.0,
            confidence_score=95.0,
            created_at=datetime.utcnow()
        )
        db.add(rel)
        
        db.commit()
        print(f"SUCCESS|REL_ID:{rel_id}|JANE_ID:{jane_id}")
        
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_relationship()
