from __future__ import annotations

from exports.report_exporter import build_docx_report, build_markdown_report


def export_markdown(cv_review: dict, qa: dict, audience: str) -> str:
    return build_markdown_report(cv_review, qa, audience=audience)


def export_docx(cv_review: dict, qa: dict, audience: str) -> bytes:
    return build_docx_report(cv_review, qa, audience=audience)
