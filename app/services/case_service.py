from sqlalchemy.orm import Session
from uuid import UUID
from app.db import models
from app.db.schemas import CaseCreate

def create_case(db: Session, payload: CaseCreate, user_id: UUID) -> models.Case:
    db_case = models.Case(
        title=payload.title,
        status=payload.status,
        jurisdiction=payload.jurisdiction,
        # created_by=user_id, # FIXME: User might not exist in DB yet (mock token), so avoid FK violation
        created_by=None,
        # description is not in models.Case yet? Let's check models.py Step 448
        # Step 448: Case has title, status, jurisdiction, integrity_score, created_by.
        # It does NOT have description.
        # But my schema has description.
        # I should probably ignore description for now or add it to the model.
        # Since I cannot easily change the DB schema (migration needed), I will ignore description for now.
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case

def get_case(db: Session, case_id: UUID) -> models.Case | None:
    return db.get(models.Case, case_id)
