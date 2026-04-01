from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TargetDomain(str, Enum):
    FE = "FE"
    BE = "BE"
    DA = "DA"
    QA = "QA"
    BA = "BA"
    AI = "AI"
    unknown = "unknown"


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    tenant_name: str
    tenant_type: str = "department"
    email: str
    full_name: str
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TenantOut(BaseModel):
    id: int
    name: str
    tenant_type: str


class LecturerOut(BaseModel):
    id: int
    tenant_id: int
    email: str
    full_name: str
    role: str


class StudentCreate(BaseModel):
    full_name: str
    student_code: str
    major: str = "unknown"
    class_id: int | None = None
    cohort_id: int | None = None
    target_domain: TargetDomain = TargetDomain.unknown


class StudentUpdate(BaseModel):
    full_name: str | None = None
    major: str | None = None
    class_id: int | None = None
    cohort_id: int | None = None
    target_domain: TargetDomain | None = None


class StudentOut(BaseModel):
    id: int
    tenant_id: int
    full_name: str
    student_code: str
    major: str
    target_domain: str


class ParsedCV(BaseModel):
    student_name: str = Field(description="Name exactly from CV, or unknown")
    email: str = Field(default="unknown")
    phone: str = Field(default="unknown")
    skills: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    unknown_fields: list[str] = Field(default_factory=list)


class CVReviewResult(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    rubric_scores: dict[str, int]
    strengths: list[str]
    gaps: list[str]
    critical_issues: list[str]
    suggested_improvements: list[str]

    @field_validator("rubric_scores")
    @classmethod
    def validate_range(cls, v: dict[str, int]) -> dict[str, int]:
        for score in v.values():
            if score < 0 or score > 10:
                raise ValueError("rubric score must be between 0 and 10")
        return v


class InterviewQuestionItem(BaseModel):
    category: Literal["intro", "technical", "behavioral", "problem_solving", "cv_deep_dive"]
    question: str
    expected_signals: list[str]
    answer_outline: list[str]
    difficulty: Literal["basic", "intermediate", "advanced"]


class InterviewQuestionSet(BaseModel):
    mode: Literal["normal", "deep"]
    target_domain: TargetDomain
    questions: list[InterviewQuestionItem]


class CVUploadResponse(BaseModel):
    cv_id: int
    version: int
    file_name: str


class CVActionRequest(BaseModel):
    cv_id: int
    domain: TargetDomain = TargetDomain.unknown


class CVReviewRequest(CVActionRequest):
    target_role: str
    jd_text: str = ""


class InterviewGenerateRequest(CVActionRequest):
    mode: Literal["normal", "deep"] = "normal"


class AnalyticsSummary(BaseModel):
    total_students: int
    total_cv_reviewed: int
    average_score: float
    total_interview_sets_generated: int


class AnalyticsSummaryResponse(BaseModel):
    summary: AnalyticsSummary


class AnalyticsDistributionResponse(BaseModel):
    score_distribution: list[dict]
    domain_distribution: list[dict]


class AnalyticsIssuesResponse(BaseModel):
    common_cv_issues: list[dict]


class AnalyticsTrendsResponse(BaseModel):
    class_comparison: list[dict]
    cohort_comparison: list[dict]
    monthly_usage_trend: list[dict]
