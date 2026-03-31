from exports.report_exporter import build_docx_report, build_markdown_report


def test_export_outputs_non_empty() -> None:
    cv = {"student_info": {"name": "A"}, "target_role": "Backend", "cv_scores": {"overall_score_100": 80}, "strengths": [], "critical_issues": [], "quick_feedback_for_student": "ok"}
    qa = {"question_set": [{"question": "Q1", "why_this_is_asked": "Why"}]}
    md = build_markdown_report(cv, qa)
    docx = build_docx_report(cv, qa)
    assert "CV Review Report" in md
    assert len(docx) > 100
