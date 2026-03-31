from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_tenant_id
from backend.core.schemas import TenantOut
from backend.storage.database import get_db
from backend.storage.models import Tenant

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("/current", response_model=TenantOut)
def current_tenant(tenant_id: int = Depends(get_current_tenant_id), db: Session = Depends(get_db)) -> TenantOut:
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).one()
    return TenantOut(id=tenant.id, name=tenant.name, tenant_type=tenant.tenant_type)
