from __future__ import annotations

import logging

from backend.core.schemas import CVReviewResult, ParsedCV
from backend.integrations.openai.adapter import OpenAIAdapter
from backend.prompts.domain_config import load_domain_config
from parsers.cv_parser import parse_cv_text
from services.review_service import build_cv_review

logger = logging.getLogger(__name__)


def parse_cv_to_structured_json(raw_text: str, domain: str, adapter: OpenAIAdapter | None = None) -> ParsedCV:
    domain_cfg = load_domain_config(domain)
    prompt = (
        "Extract CV data as JSON. Use only given CV text. "
        "Never invent facts. If missing data, use 'unknown' or 'cần bổ sung'. "
        f"Target domain rubric: {domain_cfg.get('rubric', [])}."
    )
    if adapter:
        try:
            return adapter.structured_json(system_prompt=prompt, user_payload={"cv_text": raw_text}, schema_model=ParsedCV)
        except Exception as exc:
            logger.warning("LLM parse failed, fallback to rule-based parser: %s", exc)

    parsed = parse_cv_text(raw_text)
    return ParsedCV(
        student_name=parsed.student_info.name or "unknown",
        email=parsed.student_info.email or "unknown",
        phone=parsed.student_info.phone or "unknown",
        skills=[parsed.sections.get("skills", "unknown")],
        projects=[parsed.sections.get("projects", "cần bổ sung")],
        experience=[parsed.sections.get("experience", "cần bổ sung")],
        education=[parsed.sections.get("education", "cần bổ sung")],
        unknown_fields=parsed.missing_fields,
    )


def review_cv_against_rubric(parsed: ParsedCV, jd_text: str, target_role: str, domain: str, adapter: OpenAIAdapter | None = None) -> CVReviewResult:
    domain_cfg = load_domain_config(domain)
    prompt = (
        "Review CV against rubric and JD. Use only evidence from inputs. "
        "If evidence missing, mark unknown/cần bổ sung. "
        f"Rubric keys: {domain_cfg.get('rubric', [])}."
    )

    if adapter:
        try:
            return adapter.structured_json(
                system_prompt=prompt,
                user_payload={"parsed_cv": parsed.model_dump(), "jd_text": jd_text, "target_role": target_role},
                schema_model=CVReviewResult,
            )
        except Exception as exc:
            logger.warning("LLM review failed, fallback to heuristic: %s", exc)

    legacy = parse_cv_text("\n".join([parsed.student_name, *parsed.skills, *parsed.projects, *parsed.experience]))
    review = build_cv_review(legacy, target_role=target_role, language="tiếng Việt", jd_text=jd_text)
    return CVReviewResult(
        overall_score=review.cv_scores.overall_score_100,
        rubric_scores={
            "layout_readability": review.cv_scores.layout_readability,
            "completeness": review.cv_scores.completeness,
            "role_fit": review.cv_scores.role_fit,
            "project_quality": review.cv_scores.project_quality,
            "achievement_specificity": review.cv_scores.achievement_specificity,
            "skills_quality": review.cv_scores.skills_quality,
            "language_professionalism": review.cv_scores.language_professionalism,
            "ats_friendliness": review.cv_scores.ats_friendliness,
            "keyword_alignment": review.cv_scores.keyword_alignment,
        },
        strengths=review.strengths,
        gaps=review.keyword_gap.missing_keywords,
        critical_issues=review.critical_issues,
        suggested_improvements=review.rewrite_suggestions.project_bullets,
    )
