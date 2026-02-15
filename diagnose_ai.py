from app.db.session import SessionLocal
from app.db import models
from sqlalchemy import select

def diagnose():
    db = SessionLocal()
    try:
        print("--- Database Diagnostic ---")
        
        # 1. Check total jobs
        jobs = db.query(models.IngestJob).order_by(models.IngestJob.created_at.desc()).limit(5).all()
        print(f"Recent Jobs:")
        for j in jobs:
            print(f"  Job: {j.job_id} | Case: {j.case_id} | Status: {j.status}")

        # 2. Check total entities
        entities = db.query(models.Entity).order_by(models.Entity.entity_id.desc()).limit(5).all()
        print(f"Recent Entities:")
        for e in entities:
            print(f"  Entity: {e.entity_id} | Label: {e.label} | Type: {e.entity_type}")

        # 3. Check Case-Entity Links
        links = db.query(models.CaseEntity).limit(5).all()
        print(f"Case-Entity Links:")
        for l in links:
            print(f"  Case: {l.case_id} -> Entity: {l.entity_id}")

        # 4. Check Insights
        insights = db.query(models.Insight).limit(5).all()
        print(f"Recent Insights:")
        for i in insights:
            print(f"  Insight: {i.insight_id} | Summary: {i.summary}")

    finally:
        db.close()

if __name__ == "__main__":
    diagnose()
