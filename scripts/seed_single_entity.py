from app.db.session import SessionLocal
from app.db import models
import uuid
from datetime import datetime

def seed_entity():
    db = SessionLocal()
    try:
        # 1. Check if we have a case
        case = db.query(models.Case).first()
        if not case:
            print("No cases found. Create a case first.")
            return

        # 2. Create Entity
        entity_id = uuid.uuid4()
        entity = models.Entity(
            entity_id=entity_id,
            label="John Doe",
            entity_type="person",
            risk_score=45.0,
            confidence_score=90.0,
            created_at=datetime.utcnow()
        )
        db.add(entity)
        
        # 3. Link to Case
        case_entity = models.CaseEntity(
            case_id=case.case_id,
            entity_id=entity_id,
            role_in_case="primary_suspect"
        )
        db.add(case_entity)
        
        db.commit()
        print(f"SUCCESS: Created entity 'John Doe' with ID: {entity_id}")
        print(f"Linked to Case: {case.title} ({case.case_id})")
        
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_entity()
