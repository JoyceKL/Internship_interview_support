from __future__ import annotations

import logging
import re
from io import BytesIO
from typing import Dict, List

from docx import Document
from pypdf import PdfReader

from models.schemas import ParsedCV, StudentInfo

logger = logging.getLogger(__name__)

SECTION_MAP = {
    "summary": ["summary", "objective", "mục tiêu", "giới thiệu"],
    "education": ["education", "học vấn"],
    "skills": ["skills", "kỹ năng"],
    "projects": ["projects", "dự án"],
    "experience": ["experience", "kinh nghiệm"],
    "certifications": ["certifications", "chứng chỉ"],
    "activities": ["activities", "hoạt động"],
    "awards": ["awards", "giải thưởng"],
}


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = Document(BytesIO(file_bytes))
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])


def _find_section(content: str, candidates: List[str]) -> str:
    lines = [line.strip() for line in content.splitlines()]
    for i, line in enumerate(lines):
        lower = line.lower()
        if any(c in lower for c in candidates):
            chunk: List[str] = []
            for j in range(i + 1, min(i + 14, len(lines))):
                if any(k in lines[j].lower() for v in SECTION_MAP.values() for k in v):
                    break
                if lines[j]:
                    chunk.append(lines[j])
            return "\n".join(chunk).strip()
    return ""


def parse_cv_text(cv_text: str) -> ParsedCV:
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", cv_text)
    phone_match = re.search(r"(\+?\d[\d\s\-\(\)]{8,}\d)", cv_text)
    links = re.findall(r"https?://\S+|(?:github\.com|linkedin\.com)/\S+", cv_text, flags=re.IGNORECASE)

    lines = [l.strip() for l in cv_text.splitlines() if l.strip()]
    name = lines[0] if lines else "Thiếu hoặc không nhận diện được"

    sections: Dict[str, str] = {}
    missing_fields: List[str] = []
    for sec, keys in SECTION_MAP.items():
        sections[sec] = _find_section(cv_text, keys)
        if not sections[sec]:
            missing_fields.append(sec)

    student = StudentInfo(
        name=name,
        email=email_match.group(0) if email_match else "Thiếu hoặc không nhận diện được",
        phone=phone_match.group(0) if phone_match else "Thiếu hoặc không nhận diện được",
        links=links,
    )

    if student.email.startswith("Thiếu"):
        missing_fields.append("email")
    if student.phone.startswith("Thiếu"):
        missing_fields.append("phone")

    return ParsedCV(raw_text=cv_text, student_info=student, sections=sections, missing_fields=sorted(set(missing_fields)))


def parse_cv_file(file_name: str, file_bytes: bytes) -> ParsedCV:
    lower = file_name.lower()
    try:
        if lower.endswith(".pdf"):
            text = extract_text_from_pdf(file_bytes)
        elif lower.endswith(".docx"):
            text = extract_text_from_docx(file_bytes)
        else:
            raise ValueError("Unsupported file format. Use PDF or DOCX.")
        if not text.strip():
            raise ValueError("Không thể trích xuất nội dung CV. Vui lòng kiểm tra file.")
        return parse_cv_text(text)
    except Exception as exc:
        logger.exception("Failed to parse CV")
        raise ValueError(f"Lỗi đọc CV: {exc}") from exc
