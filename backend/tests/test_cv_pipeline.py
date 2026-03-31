from __future__ import annotations


def auth_header(client):
    client.post(
        "/auth/register",
        json={
            "tenant_name": "Tenant CV",
            "tenant_type": "faculty",
            "email": "cv@example.com",
            "full_name": "CV Lecturer",
            "password": "StrongPass123",
        },
    )
    login = client.post("/auth/login", json={"email": "cv@example.com", "password": "StrongPass123"}).json()
    return {"Authorization": f"Bearer {login['access_token']}"}


def test_e2e_pipeline(client):
    headers = auth_header(client)
    student = client.post(
        "/students",
        json={"full_name": "Student 1", "student_code": "S1", "major": "SE", "target_domain": "BE"},
        headers=headers,
    ).json()

    cv_text = "Student 1\nEmail: s1@mail.com\nSkills\nPython, SQL\nProjects\nBuilt API improved 20%"
    uploaded = client.post(
        "/cv/upload",
        files={"file": ("cv.txt", cv_text.encode("utf-8"), "text/plain")},
        data={"student_id": student["id"]},
        headers=headers,
    )
    assert uploaded.status_code == 200
    cv_id = uploaded.json()["cv_id"]

    parsed = client.post(f"/cv/{cv_id}/parse", data={"domain": "BE"}, headers=headers)
    assert parsed.status_code == 200
    assert parsed.json()["student_name"] != ""

    reviewed = client.post(
        f"/cv/{cv_id}/review",
        data={"target_role": "Backend Intern", "jd_text": "python sql api", "domain": "BE"},
        headers=headers,
    )
    assert reviewed.status_code == 200

    qa = client.post(f"/interview/{cv_id}/generate", data={"mode": "normal", "domain": "BE"}, headers=headers)
    assert qa.status_code == 200
    assert len(qa.json()["questions"]) >= 10

    analytics = client.get("/analytics/dashboard", headers=headers)
    assert analytics.status_code == 200
    assert analytics.json()["summary"]["total_students"] == 1
