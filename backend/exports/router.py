from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_tenant_id
from backend.exports.service import export_docx, export_markdown
from backend.storage.database import get_db
from backend.storage.models import CVReviewResultDB, InterviewQuestionSet

router = APIRouter(prefix="/exports", tags=["exports"])


@router.get("/{cv_id}/markdown")
def markdown_report(cv_id: int, audience: str = "lecturer", tenant_id: int = Depends(get_current_tenant_id), db: Session = Depends(get_db)) -> Response:
    review = db.query(CVReviewResultDB).filter(CVReviewResultDB.cv_id == cv_id, CVReviewResultDB.tenant_id == tenant_id).order_by(CVReviewResultDB.id.desc()).first()
    qa = db.query(InterviewQuestionSet).filter(InterviewQuestionSet.cv_id == cv_id, InterviewQuestionSet.tenant_id == tenant_id).order_by(InterviewQuestionSet.id.desc()).first()
    if not review or not qa:
        raise HTTPException(status_code=404, detail="Data not ready")
    content = export_markdown(review.review_json, qa.result_json, audience=audience)
    return Response(content=content, media_type="text/markdown")


@router.get("/{cv_id}/docx")
def docx_report(cv_id: int, audience: str = "student", tenant_id: int = Depends(get_current_tenant_id), db: Session = Depends(get_db)) -> Response:
    review = db.query(CVReviewResultDB).filter(CVReviewResultDB.cv_id == cv_id, CVReviewResultDB.tenant_id == tenant_id).order_by(CVReviewResultDB.id.desc()).first()
    qa = db.query(InterviewQuestionSet).filter(InterviewQuestionSet.cv_id == cv_id, InterviewQuestionSet.tenant_id == tenant_id).order_by(InterviewQuestionSet.id.desc()).first()
    if not review or not qa:
        raise HTTPException(status_code=404, detail="Data not ready")
    content = export_docx(review.review_json, qa.result_json, audience=audience)
    return Response(content=content, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
