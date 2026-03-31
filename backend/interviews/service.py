from __future__ import annotations

import logging

from backend.core.schemas import InterviewQuestionItem, InterviewQuestionSet, ParsedCV, TargetDomain
from backend.integrations.openai.adapter import OpenAIAdapter
from backend.prompts.domain_config import load_domain_config
from services.qa_service import generate_interview_qa
from parsers.cv_parser import parse_cv_text

logger = logging.getLogger(__name__)


def generate_interview_questions(parsed: ParsedCV, mode: str, domain: str, adapter: OpenAIAdapter | None = None) -> InterviewQuestionSet:
    domain_cfg = load_domain_config(domain)
    prompt = (
        "Generate interview questions. Only use candidate CV evidence and domain focus. "
        "Do not invent achievements. If missing evidence, include 'cần bổ sung'."
    )
    normalized_mode = "deep" if mode == "deep" else "normal"

    if adapter:
        try:
            return adapter.structured_json(
                system_prompt=prompt,
                user_payload={
                    "parsed_cv": parsed.model_dump(),
                    "mode": normalized_mode,
                    "domain_focus": domain_cfg.get("interview_focus", []),
                },
                schema_model=InterviewQuestionSet,
            )
        except Exception as exc:
            logger.warning("LLM qa failed, fallback to deterministic: %s", exc)

    legacy = parse_cv_text("\n".join([parsed.student_name, *parsed.skills, *parsed.projects, *parsed.experience]))
    qa = generate_interview_qa(legacy, target_role=f"{domain} Intern", language="tiếng Việt", mode="Chuyên sâu" if normalized_mode == "deep" else "Thường")
    questions = []
    for q in qa.question_set:
        questions.append(
            InterviewQuestionItem(
                category="technical",
                question=q.question,
                expected_signals=[q.what_interviewer_looks_for],
                answer_outline=q.answer_outline,
                difficulty="intermediate" if normalized_mode == "normal" else "advanced",
            )
        )
    return InterviewQuestionSet(mode=normalized_mode, target_domain=TargetDomain(domain) if domain in TargetDomain.__members__ else TargetDomain.unknown, questions=questions)
