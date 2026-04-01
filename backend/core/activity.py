from __future__ import annotations

from sqlalchemy.orm import Session

from backend.storage.models import ActivityLog


def log_activity(
    db: Session,
    *,
    tenant_id: int,
    actor_id: int,
    action: str,
    entity_type: str,
    entity_id: int,
    meta: dict | None = None,
) -> None:
    db.add(
        ActivityLog(
            tenant_id=tenant_id,
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            meta=meta or {},
        )
    )
