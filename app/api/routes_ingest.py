from fastapi import APIRouter, UploadFile, File, Form
import hashlib
import os
from pathlib import Path

router = APIRouter()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def ingest_upload(case_id: str = Form(...), source_type: str = Form("cdr"), file: UploadFile = File(...)):
    data = await file.read()
    sha = hashlib.sha256(data).hexdigest()
    out_path = UPLOAD_DIR / f"{sha}_{file.filename}"
    out_path.write_bytes(data)
    return {
        "case_id": case_id,
        "source_type": source_type,
        "filename": file.filename,
        "sha256_hash": sha,
        "stored_as": str(out_path)
    }

@router.get("/validation/{job_id}")
def ingest_validation(job_id: str):
    return {"job_id": job_id, "status": "stub", "validation_score": 0.0}
