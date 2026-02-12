import sys
import os
from uuid import UUID

# Add app to path
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.db import models

def verify():
    db = SessionLocal()
    
    try:
        print("--- Verifying Audit Logs ---")
        logs = db.query(models.AuditLog).order_by(models.AuditLog.created_at.desc()).limit(5).all()
        for l in logs:
             print(f"[{l.created_at}] User {l.user_id} performed {l.action} on {l.target_type}:{l.target_id} (IP: {l.ip_address})")
        
        print("\n--- Verifying Ingest Validation ---")
        jobs = db.query(models.IngestJob).order_by(models.IngestJob.created_at.desc()).limit(3).all()
        for j in jobs:
            print(f"Job {j.job_id} | Status: {j.status} | Validation Score: {float(j.validation_score)}")
            
        print("\n--- Verifying Exports ---")
        exports = db.query(models.Export).order_by(models.Export.created_at.desc()).limit(3).all()
        for e in exports:
             print(f"Export {e.export_id} | Type: {e.export_type} | Hash: {e.export_hash[:16]}...")
    finally:
        db.close()

if __name__ == "__main__":
    verify()
