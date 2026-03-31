from __future__ import annotations


def register_and_login(client, email: str, tenant_name: str = "Khoa CNTT"):
    r = client.post(
        "/auth/register",
        json={
            "tenant_name": tenant_name,
            "tenant_type": "faculty",
            "email": email,
            "full_name": "Lecturer",
            "password": "StrongPass123",
        },
    )
    assert r.status_code == 200
    login = client.post("/auth/login", json={"email": email, "password": "StrongPass123"})
    assert login.status_code == 200
    return login.json()["access_token"]


def test_auth_flow(client):
    access = register_and_login(client, "l1@example.com")
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert me.status_code == 200
    assert me.json()["email"] == "l1@example.com"


def test_tenant_isolation_students(client):
    token_a = register_and_login(client, "a@example.com", "Tenant A")
    token_b = register_and_login(client, "b@example.com", "Tenant B")

    created = client.post(
        "/students",
        json={"full_name": "SV A", "student_code": "A01", "major": "IT", "target_domain": "BE"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert created.status_code == 200

    list_b = client.get("/students", headers={"Authorization": f"Bearer {token_b}"})
    assert list_b.status_code == 200
    assert list_b.json() == []
