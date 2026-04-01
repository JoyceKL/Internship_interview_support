from __future__ import annotations


def _auth(client, email: str = "contract@example.com") -> dict[str, str]:
    client.post(
        "/auth/register",
        json={
            "tenant_name": "Tenant Contract",
            "tenant_type": "faculty",
            "email": email,
            "full_name": "Contract Lecturer",
            "password": "StrongPass123",
        },
    )
    login = client.post("/auth/login", json={"email": email, "password": "StrongPass123"}).json()
    return {"Authorization": f"Bearer {login['access_token']}"}


def test_required_endpoints_contract(client):
    headers = _auth(client)
    student = client.post(
        "/students",
        json={"full_name": "Student 2", "student_code": "S2", "major": "SE", "target_domain": "FE"},
        headers=headers,
    ).json()
    uploaded = client.post(
        "/cv/upload",
        files={"file": ("cv.txt", b"Student 2\nEmail: s2@mail.com\nSkills\nHTML CSS JS", "text/plain")},
        data={"student_id": student["id"]},
        headers=headers,
    ).json()
    cv_id = uploaded["cv_id"]

    parsed = client.post("/cv/parse", json={"cv_id": cv_id, "domain": "FE"}, headers=headers)
    assert parsed.status_code == 200

    reviewed = client.post(
        "/cv/review",
        json={"cv_id": cv_id, "target_role": "FE Intern", "jd_text": "react html css", "domain": "FE"},
        headers=headers,
    )
    assert reviewed.status_code == 200

    qa = client.post("/interview/generate", json={"cv_id": cv_id, "domain": "FE", "mode": "normal"}, headers=headers)
    assert qa.status_code == 200

    assert client.get("/analytics/summary", headers=headers).status_code == 200
    assert client.get("/analytics/distribution", headers=headers).status_code == 200
    assert client.get("/analytics/issues", headers=headers).status_code == 200
    assert client.get("/analytics/trends", headers=headers).status_code == 200
