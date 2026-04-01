from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from backend.core.config import settings


def ensure_data_dirs() -> None:
    settings.cv_upload_dir.mkdir(parents=True, exist_ok=True)
    settings.jd_upload_dir.mkdir(parents=True, exist_ok=True)
    settings.exports_dir.mkdir(parents=True, exist_ok=True)


def save_upload_file(content: bytes, original_name: str, upload_dir: Path) -> Path:
    ensure_data_dirs()
    suffix = Path(original_name).suffix or ".txt"
    file_name = f"{uuid4().hex}{suffix}"
    target_path = upload_dir / file_name
    target_path.write_bytes(content)
    return target_path
