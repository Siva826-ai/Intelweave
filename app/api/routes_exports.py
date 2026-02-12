from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db import models
from app.db.session import get_db
from app.api.deps import get_current_active_user
from app.services.export_service import generate_court_pdf, build_export_manifest, write_manifest, create_export_record, sha256_file
from app.services.audit_service import log_action
from uuid import UUID
from pathlib import Path

router = APIRouter()
_guard = require_clearance(2)  # exports require higher clearance

@router.post("/pdf")
def export_pdf(payload: dict, request: Request, db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    # User clearance check is already in main or can be done here. 
    # Using specific requirement check:
    if user.clearance_level < 2:
         return {"detail": "Insufficient clearance"}

    case_str = payload.get("case_id")
    if not case_str:
        return {"detail": "case_id required"}
    case_id = UUID(case_str)
    
    pdf_path = generate_court_pdf(db, case_id, payload)
    file_hash = sha256_file(pdf_path)
    
    # Create Record & Log Action
    export_rec = create_export_record(db, case_id, "pdf", user.user_id, file_hash)
    log_action(db, user.user_id, "export_pdf", "case", str(case_id), case_id, request.client.host)

    manifest = build_export_manifest(str(case_id), [pdf_path], meta={"mode": payload.get("mode","court"), "include": payload.get("include", [])})
    manifest_path = write_manifest(str(case_id), manifest)
    
    return {
        "export_id": str(export_rec.export_id),
        "case_id": str(case_id),
        "pdf": str(pdf_path),
        "pdf_sha256": file_hash,
        "manifest": str(manifest_path)
    }

# Remove redundant hashlib_sha

@router.post("/network-snapshot")
def export_network_snapshot(payload: dict, request: Request, db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    if user.clearance_level < 2:
         return {"detail": "Insufficient clearance"}
         
    case_id_str = payload.get("case_id")
    if not case_id_str:
        return {"detail": "case_id required"}
    case_id = UUID(case_id_str)
    
    log_action(db, user.user_id, "export_network", "case", str(case_id), case_id, request.client.host)
    
    # For v1.1, return a placeholder manifest only
    manifest = build_export_manifest(str(case_id), [], meta={"mode": payload.get("mode","court"), "note":"Implement graph snapshot renderer"})
    manifest_path = write_manifest(str(case_id), manifest)
    return {"case_id": str(case_id), "manifest": str(manifest_path)}
