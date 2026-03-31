from __future__ import annotations

from backend.auth.security import get_password_hash
from backend.storage.database import SessionLocal
from backend.storage.models import ClassGroup, Cohort, Lecturer, Student, Tenant


def seed_demo() -> None:
    db = SessionLocal()
    if db.query(Tenant).count() > 0:
        db.close()
        return
    tenant = Tenant(name="CNTT Demo", tenant_type="faculty")
    db.add(tenant)
    db.flush()

    lecturer = Lecturer(tenant_id=tenant.id, email="lecturer@demo.local", full_name="Demo Lecturer", password_hash=get_password_hash("DemoPass123"))
    db.add(lecturer)
    db.flush()

    class_group = ClassGroup(tenant_id=tenant.id, code="SE01", name="Software Engineering 01")
    cohort = Cohort(tenant_id=tenant.id, year=2026, name="K26")
    db.add_all([class_group, cohort])
    db.flush()

    db.add(Student(tenant_id=tenant.id, class_id=class_group.id, cohort_id=cohort.id, full_name="Nguyen Van A", student_code="SV001", major="CNTT", target_domain="BE"))
    db.commit()
    db.close()


if __name__ == "__main__":
    seed_demo()
