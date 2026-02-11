from sqlalchemy.orm import Session
from uuid import UUID
from app.db.models import AuditLog

def log_action(
    db: Session,
    user_id: UUID,
    action: str,
    target_type: str,
    target_id: str,
    case_id: UUID | None = None
) -> AuditLog:
    """
    Log an action to the audit log.
    Strictly append-only.
    """
    log_entry = AuditLog(
        user_id=user_id,
        case_id=case_id,
        action=action,
        target_type=target_type,
        target_id=target_id
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry
