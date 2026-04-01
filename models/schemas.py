from __future__ import annotations

from typing import List, Dict
from pydantic import BaseModel, Field


class StudentInfo(BaseModel):
    name: str = "Thiếu hoặc không nhận diện được"
    student_id: str = ""
    major: str = ""
    email: str = "Thiếu hoặc không nhận diện được"
    phone: str = "Thiếu hoặc không nhận diện được"
    links: List[str] = Field(default_factory=list)


class CVScores(BaseModel):
    layout_readability: int = 0
    completeness: int = 0
    role_fit: int = 0
    project_quality: int = 0
    achievement_specificity: int = 0
    skills_quality: int = 0
    language_professionalism: int = 0
    ats_friendliness: int = 0
    keyword_alignment: int = 0
    overall_score_100: int = 0


class KeywordGap(BaseModel):
    missing_keywords: List[str] = Field(default_factory=list)
    weak_keywords: List[str] = Field(default_factory=list)
    matched_keywords: List[str] = Field(default_factory=list)


class RewriteSuggestions(BaseModel):
    summary: str = "Cần sinh viên bổ sung thông tin"
    project_bullets: List[str] = Field(default_factory=list)
    experience_bullets: List[str] = Field(default_factory=list)
    skills_reordering: List[str] = Field(default_factory=list)


class CVReviewResult(BaseModel):
    student_info: StudentInfo
    target_role: str
    language: str
    cv_scores: CVScores
    strengths: List[str] = Field(default_factory=list)
    critical_issues: List[str] = Field(default_factory=list)
    missing_sections: List[str] = Field(default_factory=list)
    keyword_gap: KeywordGap = Field(default_factory=KeywordGap)
    rewrite_suggestions: RewriteSuggestions = Field(default_factory=RewriteSuggestions)
    quick_feedback_for_student: str = ""
    detailed_feedback_for_lecturer: str = ""


class QuestionItem(BaseModel):
    category: str
    question: str
    why_this_is_asked: str
    what_interviewer_looks_for: str
    answer_outline: List[str]
    sample_answer: str
    common_mistakes: List[str]
    follow_up_questions: List[str]


class InterviewQAResult(BaseModel):
    student_info: Dict[str, object]
    target_role: str
    language: str
    question_set: List[QuestionItem]


class ParsedCV(BaseModel):
    raw_text: str
    student_info: StudentInfo
    sections: Dict[str, str]
    missing_fields: List[str] = Field(default_factory=list)
