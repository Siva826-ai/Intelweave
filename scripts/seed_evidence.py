from app.db.session import SessionLocal
from app.db import models
import uuid
from datetime import datetime, timedelta

def seed_evidence():
    db = SessionLocal()
    try:
        case_id = uuid.UUID('f4952490-64a6-4c6c-a727-f0c68f38d500') # Operation Nightfall
        
        # 1. Create Evidence Item 1 (3 days ago)
        ev1 = models.EvidenceItem(
            case_id=case_id,
            evidence_type="phone_record",
            description="Intercepted call between Suspect A and B",
            evidence_hash=uuid.uuid4().hex,
            created_at=datetime.utcnow() - timedelta(days=3)
        )
        db.add(ev1)
        
        # 2. Create Evidence Item 2 (1 day ago)
        ev2 = models.EvidenceItem(
            case_id=case_id,
            evidence_type="location_log",
            description="Tower ping in Sector 7",
            evidence_hash=uuid.uuid4().hex,
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        db.add(ev2)
        
        db.commit()
        print("SUCCESS: Seeded 2 evidence items for case.")
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_evidence()
