from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_tenant_id, get_current_user
from backend.core.schemas import CVReviewResult, CVUploadResponse, ParsedCV
from backend.cv.service import parse_cv_to_structured_json, review_cv_against_rubric
from backend.storage.database import get_db
from backend.storage.models import CV, CVParsingResult, CVReviewResultDB, Lecturer, Student

router = APIRouter(prefix="/cv", tags=["cv"])


@router.post("/upload", response_model=CVUploadResponse)
async def upload_cv(
    student_id: int = Form(...),
    file: UploadFile = File(...),
    tenant_id: int = Depends(get_current_tenant_id),
    current_user: Lecturer = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CVUploadResponse:
    student = db.query(Student).filter(Student.id == student_id, Student.tenant_id == tenant_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    raw_text = (await file.read()).decode("utf-8", errors="ignore")
    latest_version = db.query(func.max(CV.version)).filter(CV.student_id == student_id).scalar() or 0
    cv = CV(
        tenant_id=tenant_id,
        student_id=student_id,
        version=latest_version + 1,
        file_name=file.filename or "uploaded_cv.txt",
        raw_text=raw_text,
        created_by=current_user.id,
    )
    db.add(cv)
    db.commit()
    db.refresh(cv)
    return CVUploadResponse(cv_id=cv.id, version=cv.version, file_name=cv.file_name)


@router.post("/{cv_id}/parse", response_model=ParsedCV)
def parse_cv(cv_id: int, domain: str = Form("unknown"), tenant_id: int = Depends(get_current_tenant_id), db: Session = Depends(get_db)) -> ParsedCV:
    cv = db.query(CV).filter(CV.id == cv_id, CV.tenant_id == tenant_id).first()
    if cv is None:
        raise HTTPException(status_code=404, detail="CV not found")
    parsed = parse_cv_to_structured_json(cv.raw_text, domain=domain)
    db.add(CVParsingResult(tenant_id=tenant_id, cv_id=cv.id, version=cv.version, parsed_json=parsed.model_dump()))
    db.commit()
    return parsed


@router.post("/{cv_id}/review", response_model=CVReviewResult)
def review_cv(
    cv_id: int,
    target_role: str = Form(...),
    jd_text: str = Form(""),
    domain: str = Form("unknown"),
    tenant_id: int = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
) -> CVReviewResult:
    cv = db.query(CV).filter(CV.id == cv_id, CV.tenant_id == tenant_id).first()
    if cv is None:
        raise HTTPException(status_code=404, detail="CV not found")
    parsed = parse_cv_to_structured_json(cv.raw_text, domain=domain)
    review = review_cv_against_rubric(parsed, jd_text=jd_text, target_role=target_role, domain=domain)
    db.add(CVReviewResultDB(tenant_id=tenant_id, cv_id=cv.id, version=cv.version, review_json=review.model_dump(), score=review.overall_score))
    db.commit()
    return review
