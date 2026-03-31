from __future__ import annotations

from backend.exports.service import export_docx, export_markdown


def test_exports_non_empty():
    cv = {"student_info": {"name": "A"}, "target_role": "BE", "cv_scores": {"overall_score_100": 70}, "strengths": [], "critical_issues": [], "quick_feedback_for_student": "ok"}
    qa = {"question_set": [{"question": "Q1", "why_this_is_asked": "W"}]}
    assert "CV Review Report" in export_markdown(cv, qa, "lecturer")
    assert len(export_docx(cv, qa, "student")) > 100
