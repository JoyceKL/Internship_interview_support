from __future__ import annotations

import json
from pathlib import Path


DOMAIN_FILE_MAP = {
    "FE": "fe.json",
    "BE": "be.json",
    "DA": "da.json",
    "QA": "qa.json",
    "BA": "ba.json",
    "AI": "ai.json",
}


def load_domain_config(domain: str) -> dict:
    key = domain.upper()
    file_name = DOMAIN_FILE_MAP.get(key)
    if not file_name:
        return {"domain": "unknown", "rubric": [], "keywords": [], "checklist": [], "interview_focus": []}
    path = Path(__file__).parent / "domains" / file_name
    return json.loads(path.read_text(encoding="utf-8"))
