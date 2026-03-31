from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_tenant_id
from backend.core.schemas import LecturerOut
from backend.storage.database import get_db
from backend.storage.models import Lecturer

router = APIRouter(prefix="/lecturers", tags=["lecturers"])


@router.get("", response_model=list[LecturerOut])
def list_lecturers(tenant_id: int = Depends(get_current_tenant_id), db: Session = Depends(get_db)) -> list[LecturerOut]:
    rows = db.query(Lecturer).filter(Lecturer.tenant_id == tenant_id).all()
    return [LecturerOut(id=r.id, tenant_id=r.tenant_id, email=r.email, full_name=r.full_name, role=r.role.value) for r in rows]
