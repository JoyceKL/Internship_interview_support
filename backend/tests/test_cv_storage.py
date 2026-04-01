from __future__ import annotations

from pathlib import Path


def _auth(client, email: str = "storage@example.com") -> dict[str, str]:
    client.post(
        "/auth/register",
        json={
            "tenant_name": "Tenant Storage",
            "tenant_type": "faculty",
            "email": email,
            "full_name": "Storage Lecturer",
            "password": "StrongPass123",
        },
    )
    login = client.post("/auth/login", json={"email": email, "password": "StrongPass123"}).json()
    return {"Authorization": f"Bearer {login['access_token']}"}


def test_cv_upload_saved_to_filesystem(client, db_session):
    headers = _auth(client)
    student = client.post(
        "/students",
        json={"full_name": "Student Storage", "student_code": "SS1", "major": "SE", "target_domain": "FE"},
        headers=headers,
    ).json()
    upload = client.post(
        "/cv/upload",
        files={"file": ("cv.txt", b"Storage Student\nSkills: Python", "text/plain")},
        data={"student_id": student["id"]},
        headers=headers,
    )
    assert upload.status_code == 200
    cv_id = upload.json()["cv_id"]

    from backend.storage.models import CV

    row = db_session.query(CV).filter(CV.id == cv_id).first()
    assert row is not None
    assert row.file_path
    assert Path(row.file_path).exists()
    assert row.file_size > 0
