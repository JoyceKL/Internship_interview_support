from parsers.cv_parser import parse_cv_text
from services.scoring import compute_scores


def test_scoring_returns_valid_range() -> None:
    parsed = parse_cv_text("""A\nEmail:a@b.com\nSkills\nPython\nProjects\n- Built x by 20%""")
    scores, strengths, issues, _, _ = compute_scores(parsed, "Backend Intern", "")
    assert 0 <= scores.overall_score_100 <= 100
    assert len(strengths) == 5
    assert len(issues) == 5
