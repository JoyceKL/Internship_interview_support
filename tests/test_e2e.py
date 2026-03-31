from parsers.cv_parser import parse_cv_text
from services.qa_service import generate_interview_qa
from services.review_service import build_cv_review


def test_end_to_end_happy_path() -> None:
    parsed = parse_cv_text("""Jane\nEmail: jane@mail.com\nSummary\nBackend student\nSkills\nPython, SQL\nProjects\n- Built API improved 30%""")
    review = build_cv_review(parsed, "Backend Intern", "tiếng Việt", "python sql api")
    qa = generate_interview_qa(parsed, "Backend Intern", "tiếng Việt", "Thường")
    assert review.cv_scores.overall_score_100 >= 0
    assert len(qa.question_set) == 15
