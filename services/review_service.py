from __future__ import annotations

import logging
from typing import Optional

from models.schemas import CVReviewResult
from models.schemas import ParsedCV
from services.scoring import build_rewrite_suggestions, compute_scores

logger = logging.getLogger(__name__)


def build_cv_review(parsed: ParsedCV, target_role: str, language: str, jd_text: str = "", lecturer_notes: str = "") -> CVReviewResult:
    scores, strengths, issues, missing_sections, gaps = compute_scores(parsed, target_role, jd_text)

    quick = (
        f"Tổng điểm hiện tại: {scores.overall_score_100}/100. "
        "Ưu tiên sửa: phần summary, mô tả dự án có số liệu, và tối ưu keyword theo JD."
    )
    detail = (
        "Đánh giá này dựa trên dữ liệu hiện có trong CV/JD. "
        "Không bổ sung thông tin ngoài nguồn. "
        f"Ghi chú giảng viên: {lecturer_notes or 'Không có'}"
    )

    rewrite = build_rewrite_suggestions(parsed, target_role)

    return CVReviewResult(
        student_info=parsed.student_info,
        target_role=target_role,
        language=language,
        cv_scores=scores,
        strengths=strengths,
        critical_issues=issues,
        missing_sections=missing_sections,
        keyword_gap=gaps,
        rewrite_suggestions=rewrite,
        quick_feedback_for_student=quick,
        detailed_feedback_for_lecturer=detail,
    )
