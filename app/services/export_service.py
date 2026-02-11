from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session
from app.db.models import Export
from app.services.audit_service import log_action

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

EXPORT_DIR = Path("exports")
EXPORT_DIR.mkdir(exist_ok=True)

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def generate_court_pdf(case_id: str, payload: dict) -> Path:
    """Generate a minimal court-safe PDF: no AI suggestions; includes hashes and timestamps."""
    out = EXPORT_DIR / f"court_{case_id}_{int(datetime.utcnow().timestamp())}.pdf"
    c = canvas.Canvas(str(out), pagesize=A4)
    w, h = A4
    y = h - 60

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "IntelWeave™ — Court Mode Evidence Pack")
    y -= 28

    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Case ID: {case_id}")
    y -= 18
    c.drawString(50, y, f"Generated (UTC): {datetime.utcnow().isoformat()}")
    y -= 18
    c.drawString(50, y, "Mode: Court (Read-only)")
    y -= 22

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Included Sections")
    y -= 18
    c.setFont("Helvetica", 11)
    include = payload.get("include") or ["timeline", "network", "insights", "evidence_hashes"]
    for item in include:
        c.drawString(70, y, f"• {item}")
        y -= 16
        if y < 90:
            c.showPage()
            y = h - 60

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y-10, "Integrity Notes")
    y -= 30
    c.setFont("Helvetica", 11)
    notes = [
        "This pack contains evidence-backed summaries only.",
        "AI suggestions are excluded in Court Mode.",
        "All files are hash-anchored for traceability."
    ]
    for n in notes:
        c.drawString(70, y, f"• {n}")
        y -= 16

    c.showPage()
    c.save()
    return out

def build_export_manifest(case_id: str, files: list[Path], meta: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "generated_utc": datetime.utcnow().isoformat(),
        "files": [{"name": f.name, "sha256": sha256_file(f)} for f in files],
        "meta": meta,
    }

def write_manifest(case_id: str, manifest: dict[str, Any]) -> Path:
    out = EXPORT_DIR / f"manifest_{case_id}_{int(datetime.utcnow().timestamp())}.json"
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return out

def create_export_record(
    db: Session,
    case_id: UUID,
    export_type: str,
    user_id: UUID,
    file_hash: str
) -> Export:
    export = Export(
        case_id=case_id,
        export_type=export_type,
        requested_by=user_id,
        export_hash=file_hash,
        created_at=datetime.utcnow()
    )
    db.add(export)
    db.commit()
    db.refresh(export)
    
    log_action(db, user_id, "create", "export", str(export.export_id), case_id)
    return export
