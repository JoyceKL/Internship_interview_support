from models.schemas import CVReviewResult, CVScores, StudentInfo


def test_cv_review_schema_validation() -> None:
    obj = CVReviewResult(
        student_info=StudentInfo(name="A"),
        target_role="Backend Intern",
        language="tiếng Việt",
        cv_scores=CVScores(overall_score_100=50),
    )
    assert obj.target_role == "Backend Intern"
