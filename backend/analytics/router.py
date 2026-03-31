from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_tenant_id
from backend.core.schemas import AnalyticsResponse, AnalyticsSummary
from backend.storage.database import get_db
from backend.storage.models import CVReviewResultDB, InterviewQuestionSet, Student

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=AnalyticsResponse)
def dashboard(
    class_id: int | None = None,
    cohort_id: int | None = None,
    domain: str | None = None,
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    tenant_id: int = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
) -> AnalyticsResponse:
    student_query = db.query(Student).filter(Student.tenant_id == tenant_id)
    if class_id:
        student_query = student_query.filter(Student.class_id == class_id)
    if cohort_id:
        student_query = student_query.filter(Student.cohort_id == cohort_id)
    if domain:
        student_query = student_query.filter(Student.target_domain == domain)

    student_ids = [s.id for s in student_query.all()]

    review_query = db.query(CVReviewResultDB).filter(CVReviewResultDB.tenant_id == tenant_id)
    if date_from:
        review_query = review_query.filter(CVReviewResultDB.created_at >= date_from)
    if date_to:
        review_query = review_query.filter(CVReviewResultDB.created_at <= date_to)

    reviews = review_query.all()
    avg_score = round(sum(r.score for r in reviews) / len(reviews), 2) if reviews else 0.0

    score_distribution = [{"bucket": f"{i}-{i+9}", "count": sum(1 for r in reviews if i <= r.score <= i + 9)} for i in range(0, 100, 10)]

    domain_distribution = [
        {"domain": d, "count": c}
        for d, c in db.query(Student.target_domain, func.count(Student.id))
        .filter(Student.tenant_id == tenant_id)
        .group_by(Student.target_domain)
        .all()
    ]

    issue_counter: dict[str, int] = {}
    for r in reviews:
        for issue in r.review_json.get("critical_issues", []):
            issue_counter[issue] = issue_counter.get(issue, 0) + 1
    common_issues = [{"issue": k, "count": v} for k, v in sorted(issue_counter.items(), key=lambda x: x[1], reverse=True)[:10]]

    class_cmp = [{"class_id": cid, "count": cnt} for cid, cnt in db.query(Student.class_id, func.count(Student.id)).filter(Student.tenant_id == tenant_id).group_by(Student.class_id).all()]
    cohort_cmp = [{"cohort_id": cid, "count": cnt} for cid, cnt in db.query(Student.cohort_id, func.count(Student.id)).filter(Student.tenant_id == tenant_id).group_by(Student.cohort_id).all()]

    monthly = [
        {"month": m or "unknown", "count": c}
        for m, c in db.query(func.strftime("%Y-%m", CVReviewResultDB.created_at), func.count(CVReviewResultDB.id))
        .filter(CVReviewResultDB.tenant_id == tenant_id)
        .group_by(func.strftime("%Y-%m", CVReviewResultDB.created_at))
        .all()
    ]

    summary = AnalyticsSummary(
        total_students=len(student_ids),
        total_cv_reviewed=len(reviews),
        average_score=avg_score,
        total_interview_sets_generated=db.query(InterviewQuestionSet).filter(InterviewQuestionSet.tenant_id == tenant_id).count(),
    )
    return AnalyticsResponse(
        summary=summary,
        score_distribution=score_distribution,
        domain_distribution=domain_distribution,
        common_cv_issues=common_issues,
        class_comparison=class_cmp,
        cohort_comparison=cohort_cmp,
        monthly_usage_trend=monthly,
    )
