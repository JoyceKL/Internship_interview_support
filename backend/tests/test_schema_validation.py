from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.core.schemas import CVReviewResult, InterviewQuestionSet


def test_review_schema_rejects_invalid_score():
    with pytest.raises(ValidationError):
        CVReviewResult(
            overall_score=80,
            rubric_scores={"project_quality": 12},
            strengths=[],
            gaps=[],
            critical_issues=[],
            suggested_improvements=[],
        )


def test_interview_schema_valid_mode():
    obj = InterviewQuestionSet.model_validate(
        {
            "mode": "normal",
            "target_domain": "BE",
            "questions": [
                {
                    "category": "technical",
                    "question": "API là gì?",
                    "expected_signals": ["Hiểu request/response"],
                    "answer_outline": ["Định nghĩa", "Ví dụ"],
                    "difficulty": "basic",
                }
            ],
        }
    )
    assert obj.mode == "normal"
