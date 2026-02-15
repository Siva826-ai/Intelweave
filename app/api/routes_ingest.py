from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Request
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.db.session import get_db
from app.services import ingest_service, agent_service
from app.db.schemas import IngestJobCreate, IngestJobOut, DataResponse

from app.db import models
from app.api.deps import get_current_active_user

router = APIRouter()


@router.post("/upload")
def upload_files(
    case_id: UUID = Form(...),
    source_type: str = Form(...),
    file: List[UploadFile] = File(...),
    request: Request = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_active_user)
):
    # User is guaranteed to exist by get_current_active_user

    # 1. Create Ingest Job (New Architecture Requirement)
    job_data = IngestJobCreate(source_type=source_type)
    ip = request.client.host if request else None
    job = ingest_service.create_ingest_job(db, case_id, job_data, user.user_id, ip_address=ip)

    processed_files = []

    
    for f in file:
        content = f.file.read()
        
        # Calculate SHA256 (Compliance)
        import hashlib
        file_hash = hashlib.sha256(content).hexdigest()
        
        # Track file in DB (Compliance)
        file_record = ingest_service.add_file_to_job(
            db, 
            job.job_id, 
            f.filename, 
            f.content_type or "application/octet-stream", 
            file_hash, 
            row_count=0 # Placeholder
        )
        
        processed_files.append({
            "filename": f.filename,
            "status": "uploaded",
            "file_id": str(file_record.file_id),
            "job_id": str(job.job_id)
        })
        
        # 4. Trigger Forensic AI Agent (New Intelligence Layer)
        try:
            # Decode content for agent analysis
            text_content = content.decode("utf-8", errors="ignore")
            agent_service.run_forensic_discovery(db, job.job_id, text_content)
        except Exception as e:
            # Log error but don't fail upload
            print(f"Agent discovery failed: {e}")
            
    return {
        "message": "Files uploaded and ingest job created",
        "job_id": str(job.job_id),
        "files": processed_files
    }

@router.get("/validation/{job_id}")
def get_ingest_validation(job_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    job = db.get(models.IngestJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    files = db.query(models.IngestFile).filter(models.IngestFile.job_id == job_id).all()
    
    return {
        "job_id": str(job.job_id),
        "status": job.status,
        "source_type": job.source_type,
        "validation_score": float(job.validation_score),
        "created_at": job.created_at.isoformat(),
        "files": [
            {
                "file_id": str(f.file_id),
                "filename": f.filename,
                "status": "valid", 
                "row_count": f.row_count,
                "hash": f.sha256_hash
            } for f in files
        ]
    }
