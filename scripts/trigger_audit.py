import sys
import os
import requests

# For local triggering (assuming API is at localhost:8000)
# But we can also do it via the service layer directly in a script if we want to avoid network dependencies.
# Let's do it via service layer to be sure.

sys.path.append(os.getcwd())
from app.db.session import SessionLocal
from app.db import models
from app.services import audit_service, ingest_service
from uuid import uuid4

def trigger():
    db = SessionLocal()
    try:
        # 1. Simulate an audit log with IP
        user = db.query(models.User).first()
        if user:
            print(f"Triggering audit log for user {user.email}...")
            audit_service.log_action(db, user.user_id, "verify_test", "system", "test_id", ip_address="127.0.0.1")
        
        # 2. Simulate an ingest job with validation
        case = db.query(models.Case).first()
        if case:
            print(f"Triggering ingest job for case {case.title}...")
            from app.db.schemas import IngestJobCreate
            job = ingest_service.create_ingest_job(db, case.case_id, IngestJobCreate(source_type="test"), user.user_id, "10.0.0.1")
            ingest_service.add_file_to_job(db, job.job_id, "test.csv", "text/csv", "abc123hash", row_count=100)
            
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    trigger()
