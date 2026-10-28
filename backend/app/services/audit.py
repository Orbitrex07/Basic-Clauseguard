from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.db.models import AuditLog


def log_audit_event(
    db: Session,
    action: str,
    user_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    log_entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details or {},
        ip_address=ip_address
    )
    db.add(log_entry)
    db.commit()
    return log_entry
