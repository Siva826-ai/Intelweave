from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.db.session import get_db
from app.services import ingest_service
from app.db.schemas import IngestJobCreate

router = APIRouter()

@router.post("/upload")
def upload_files(
    case_id: UUID = Form(...),
    source_type: str = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    # 1. Create Ingest Job (New Architecture Requirement)
    job_data = IngestJobCreate(source_type=source_type)
    # Using a placeholder user_id as auth context is not yet fully available in this snippet
    user_id = UUID("00000000-0000-0000-0000-000000000000") 
    job = ingest_service.create_ingest_job(db, case_id, job_data, user_id)

    processed_files = []
    
    # 2. Process Files (Integrating with existing flow assumption)
    for file in files:
        content = file.file.read()
        
        # Calculate SHA256 (Compliance)
        import hashlib
        file_hash = hashlib.sha256(content).hexdigest()
        
        # Track file in DB (Compliance)
        file_record = ingest_service.add_file_to_job(
            db, 
            job.job_id, 
            file.filename, 
            file.content_type or "application/octet-stream", 
            file_hash, 
            row_count=0 # Placeholder
        )
        
        processed_files.append({
            "filename": file.filename,
            "status": "uploaded",
            "file_id": str(file_record.file_id),
            "job_id": str(job.job_id)
        })
        
    return {
        "message": "Files uploaded and ingest job created",
        "job_id": str(job.job_id),
        "files": processed_files
    }
