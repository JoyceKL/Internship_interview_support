from __future__ import annotations

import re
from typing import Dict, List, Tuple

from models.schemas import CVScores, ParsedCV, KeywordGap

ROLE_KEYWORDS = {
    "Frontend Intern": ["react", "javascript", "typescript", "html", "css", "ui"],
    "Backend Intern": ["python", "java", "api", "database", "sql", "backend"],
    "Fullstack Intern": ["frontend", "backend", "api", "react", "database", "fullstack"],
    "Data Analyst Intern": ["sql", "excel", "power bi", "python", "analysis", "dashboard"],
    "QA Intern": ["testing", "test case", "bug", "automation", "selenium", "qa"],
    "Business Analyst Intern": ["requirement", "stakeholder", "process", "analysis", "user story"],
    "AI/ML Intern": ["python", "machine learning", "model", "pandas", "scikit", "llm"],
}

ACTION_VERBS = ["built", "developed", "implemented", "optimized", "designed", "created", "improved", "analyzed"]


def _score_section_presence(parsed: ParsedCV) -> int:
    required = ["summary", "education", "skills", "projects", "experience"]
    present = sum(1 for sec in required if parsed.sections.get(sec))
    return min(10, int((present / len(required)) * 10))


def _count_numeric_evidence(text: str) -> int:
    return len(re.findall(r"\b\d+(?:\.\d+)?%?\b", text))


def keyword_gap(cv_text: str, jd_text: str, role: str) -> KeywordGap:
    source = (jd_text or "") + " " + " ".join(ROLE_KEYWORDS.get(role, []))
    keywords = {k.lower() for k in re.findall(r"[a-zA-Z\+#\.]{3,}", source)}
    cv_tokens = {k.lower() for k in re.findall(r"[a-zA-Z\+#\.]{3,}", cv_text)}
    matched = sorted(k for k in keywords if k in cv_tokens)
    missing = sorted(k for k in keywords if k not in cv_tokens)
    weak = [k for k in matched if cv_text.lower().count(k) == 1][:10]
    return KeywordGap(missing_keywords=missing[:20], weak_keywords=weak, matched_keywords=matched[:20])


def compute_scores(parsed: ParsedCV, target_role: str, jd_text: str) -> Tuple[CVScores, List[str], List[str], List[str], KeywordGap]:
    text = parsed.raw_text.lower()
    gaps = keyword_gap(parsed.raw_text, jd_text, target_role)

    layout_readability = 8 if len(parsed.raw_text.splitlines()) > 12 else 5
    completeness = _score_section_presence(parsed)
    role_fit = min(10, max(2, 10 - len(gaps.missing_keywords) // 4))
    project_quality = 8 if parsed.sections.get("projects") else 3
    achievement_specificity = min(10, max(2, _count_numeric_evidence(parsed.raw_text) // 2 + 3))
    skills_quality = 8 if parsed.sections.get("skills") and ("," in parsed.sections["skills"] or "-" in parsed.sections["skills"]) else 4
    language_professionalism = 9 if "i am" not in text else 6
    ats_friendliness = 8 if any(h in text for h in ["experience", "education", "skills"]) else 4
    keyword_alignment = min(10, max(1, len(gaps.matched_keywords) // 2))

    issues: List[str] = []
    strengths: List[str] = []
    missing = parsed.missing_fields.copy()

    if not parsed.sections.get("projects"):
        issues.append("Thiếu phần dự án, giảm khả năng chứng minh năng lực thực tế.")
    else:
        strengths.append("Có phần dự án giúp nhà tuyển dụng đánh giá năng lực triển khai.")

    if not any("github" in l.lower() or "portfolio" in l.lower() for l in parsed.student_info.links):
        issues.append("Thiếu GitHub/Portfolio cho nhóm ngành CNTT.")
    else:
        strengths.append("Có liên kết GitHub/Portfolio hỗ trợ kiểm chứng năng lực.")

    if _count_numeric_evidence(parsed.raw_text) < 2:
        issues.append("Mô tả thiếu số liệu/minh chứng định lượng.")
    else:
        strengths.append("Có sử dụng số liệu giúp mô tả thành tựu cụ thể hơn.")

    summary = parsed.sections.get("summary", "")
    if len(summary.split()) < 20:
        issues.append("Summary ngắn hoặc chung chung, cần viết rõ mục tiêu và năng lực.")

    if parsed.sections.get("skills") and ":" not in parsed.sections["skills"] and "\n" not in parsed.sections["skills"]:
        issues.append("Kỹ năng chưa phân nhóm rõ ràng (ngôn ngữ, framework, công cụ).")

    bullets = [line for line in parsed.raw_text.splitlines() if line.strip().startswith(("-", "•"))]
    long_bullets = [b for b in bullets if len(b.split()) > 28]
    if long_bullets:
        issues.append("Có bullet quá dài và lan man, cần rút gọn theo action + result.")

    if any(v in text for v in ACTION_VERBS):
        strengths.append("Mô tả có dùng động từ hành động.")
    else:
        issues.append("Thiếu động từ hành động trong mô tả dự án/kinh nghiệm.")

    while len(strengths) < 5:
        strengths.append("Cần sinh viên bổ sung thông tin để đánh giá sâu hơn.")
    while len(issues) < 5:
        issues.append("Cần sinh viên bổ sung thông tin.")

    overall = int(round(sum([
        layout_readability,
        completeness,
        role_fit,
        project_quality,
        achievement_specificity,
        skills_quality,
        language_professionalism,
        ats_friendliness,
        keyword_alignment,
    ]) / 90 * 100))

    scores = CVScores(
        layout_readability=layout_readability,
        completeness=completeness,
        role_fit=role_fit,
        project_quality=project_quality,
        achievement_specificity=achievement_specificity,
        skills_quality=skills_quality,
        language_professionalism=language_professionalism,
        ats_friendliness=ats_friendliness,
        keyword_alignment=keyword_alignment,
        overall_score_100=overall,
    )
    return scores, strengths[:5], issues[:5], missing, gaps


def build_rewrite_suggestions(parsed: ParsedCV, target_role: str) -> Dict[str, List[str] | str]:
    summary = (
        f"Ứng viên định hướng {target_role}, có nền tảng từ học vấn và dự án đã nêu. "
        "Cần sinh viên bổ sung thông tin về tác động, quy mô và kết quả đo lường."
    )
    project_bullets = [
        "Designed and implemented [feature] using [tech], improving [metric] by [x]%.",
        "Collaborated with [team size] to deliver [project outcome] within [timeline].",
        "Resolved [problem] by applying [method], reducing [issue] by [x]%.",
    ]
    experience_bullets = [
        "Supported [team/function] in [task], resulting in [measurable impact].",
        "Automated [process] using [tool], saving [x] hours/week.",
        "Documented [artifact] to improve handover and team efficiency.",
    ]
    skills_reordering = [
        "Programming Languages",
        "Frameworks/Libraries",
        "Databases",
        "Tools & Platforms",
        "Soft Skills",
    ]
    return {
        "summary": summary,
        "project_bullets": project_bullets,
        "experience_bullets": experience_bullets,
        "skills_reordering": skills_reordering,
    }
