from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_user
from backend.auth.security import create_token, get_password_hash, verify_password
from backend.core.config import settings
from backend.core.schemas import LecturerOut, LoginRequest, RefreshRequest, RegisterRequest, TokenPair
from backend.storage.database import get_db
from backend.storage.models import Lecturer, Tenant

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=LecturerOut)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> LecturerOut:
    if db.query(Lecturer).filter(Lecturer.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    tenant = db.query(Tenant).filter(Tenant.name == payload.tenant_name).first()
    if tenant is None:
        tenant = Tenant(name=payload.tenant_name, tenant_type=payload.tenant_type)
        db.add(tenant)
        db.flush()

    lecturer = Lecturer(
        tenant_id=tenant.id,
        email=payload.email,
        full_name=payload.full_name,
        password_hash=get_password_hash(payload.password),
    )
    db.add(lecturer)
    db.commit()
    db.refresh(lecturer)
    return LecturerOut(id=lecturer.id, tenant_id=lecturer.tenant_id, email=lecturer.email, full_name=lecturer.full_name, role=lecturer.role.value)


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenPair:
    user = db.query(Lecturer).filter(Lecturer.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return TokenPair(
        access_token=create_token(str(user.id), user.tenant_id, "access", settings.access_token_expire_minutes),
        refresh_token=create_token(str(user.id), user.tenant_id, "refresh", settings.refresh_token_expire_minutes),
    )


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest) -> TokenPair:
    from backend.auth.security import decode_token

    decoded = decode_token(payload.refresh_token)
    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user_id = decoded["sub"]
    tenant_id = int(decoded["tenant_id"])
    return TokenPair(
        access_token=create_token(str(user_id), tenant_id, "access", settings.access_token_expire_minutes),
        refresh_token=create_token(str(user_id), tenant_id, "refresh", settings.refresh_token_expire_minutes),
    )


@router.get("/me", response_model=LecturerOut)
def me(current_user: Lecturer = Depends(get_current_user)) -> LecturerOut:
    return LecturerOut(
        id=current_user.id,
        tenant_id=current_user.tenant_id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.value,
    )
