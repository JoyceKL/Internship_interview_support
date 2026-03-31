from parsers.cv_parser import parse_cv_text


def test_parse_cv_text_extracts_basic_fields() -> None:
    text = """John Doe\nEmail: john@example.com\nPhone: +1 222 333 4444\nSkills\nPython, SQL\nProjects\n- Built API"""
    parsed = parse_cv_text(text)
    assert parsed.student_info.name == "John Doe"
    assert parsed.student_info.email == "john@example.com"
    assert "skills" not in parsed.missing_fields
