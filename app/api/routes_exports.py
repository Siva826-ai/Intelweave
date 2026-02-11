from fastapi import APIRouter, Depends
from app.core.security import require_clearance
from app.services.export_service import generate_court_pdf, build_export_manifest, write_manifest
from pathlib import Path

router = APIRouter()
_guard = require_clearance(2)  # exports require higher clearance

@router.post("/pdf")
def export_pdf(payload: dict, _=Depends(_guard)):
    case_id = payload.get("case_id")
    if not case_id:
        return {"detail": "case_id required"}
    pdf_path = generate_court_pdf(case_id, payload)
    manifest = build_export_manifest(case_id, [pdf_path], meta={"mode": payload.get("mode","court"), "include": payload.get("include", [])})
    manifest_path = write_manifest(case_id, manifest)
    return {
        "case_id": case_id,
        "pdf": str(pdf_path),
        "pdf_sha256": manifest["files"][0]["sha256"],
        "manifest": str(manifest_path),
        "manifest_sha256": hashlib_sha(manifest_path)
    }

def hashlib_sha(p: Path) -> str:
    import hashlib
    h=hashlib.sha256()
    with p.open("rb") as f:
        h.update(f.read())
    return h.hexdigest()

@router.post("/network-snapshot")
def export_network_snapshot(payload: dict, _=Depends(_guard)):
    # stub for graph snapshot packaging
    case_id = payload.get("case_id")
    if not case_id:
        return {"detail": "case_id required"}
    # For v1.1, return a placeholder manifest only
    manifest = build_export_manifest(case_id, [], meta={"mode": payload.get("mode","court"), "note":"Implement graph snapshot renderer"})
    manifest_path = write_manifest(case_id, manifest)
    return {"case_id": case_id, "manifest": str(manifest_path), "manifest_sha256": hashlib_sha(manifest_path)}
