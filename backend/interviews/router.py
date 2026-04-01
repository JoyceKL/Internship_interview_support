from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_tenant_id
from backend.core.schemas import InterviewGenerateRequest, InterviewQuestionSet
from backend.cv.service import parse_cv_to_structured_json
from backend.interviews.service import generate_interview_questions
from backend.storage.database import get_db
from backend.storage.models import CV, InterviewQuestionSet as InterviewQuestionSetDB

router = APIRouter(prefix="/interview", tags=["interview"])


@router.post("/{cv_id}/generate", response_model=InterviewQuestionSet)
def generate(
    cv_id: int,
    mode: str = Form("normal"),
    domain: str = Form("unknown"),
    tenant_id: int = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
) -> InterviewQuestionSet:
    cv = db.query(CV).filter(CV.id == cv_id, CV.tenant_id == tenant_id).first()
    if cv is None:
        raise HTTPException(status_code=404, detail="CV not found")
    parsed = parse_cv_to_structured_json(cv.raw_text, domain=domain)
    result = generate_interview_questions(parsed, mode=mode, domain=domain)
    latest = db.query(func.max(InterviewQuestionSetDB.version)).filter(InterviewQuestionSetDB.cv_id == cv_id).scalar() or 0
    db.add(
        InterviewQuestionSetDB(
            tenant_id=tenant_id,
            cv_id=cv_id,
            mode="deep" if mode == "deep" else "normal",
            version=latest + 1,
            result_json=result.model_dump(),
        )
    )
    db.commit()
    return result


@router.post("/generate", response_model=InterviewQuestionSet)
def generate_by_payload(
    payload: InterviewGenerateRequest,
    tenant_id: int = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
) -> InterviewQuestionSet:
    return generate(payload.cv_id, payload.mode, payload.domain.value, tenant_id, db)
