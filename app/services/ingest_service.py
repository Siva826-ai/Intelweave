from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from app.db.models import IngestJob, IngestFile
from app.db.schemas import IngestJobCreate
from app.services.audit_service import log_action

def create_ingest_job(db: Session, case_id: UUID, job_data: IngestJobCreate, user_id: UUID) -> IngestJob:
    job = IngestJob(
        case_id=case_id,
        source_type=job_data.source_type,
        status="queued",
        created_at=datetime.utcnow()
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    log_action(db, user_id, "create", "ingest_job", str(job.job_id), case_id)
    return job

def add_file_to_job(
    db: Session, 
    job_id: UUID, 
    filename: str, 
    file_type: str, 
    file_hash: str,
    row_count: int
) -> IngestFile:
    file_record = IngestFile(
        job_id=job_id,
        filename=filename,
        file_type=file_type,
        sha256_hash=file_hash,
        row_count=row_count,
        created_at=datetime.utcnow()
    )
    db.add(file_record)
    db.commit()
    db.refresh(file_record)
    return file_record
