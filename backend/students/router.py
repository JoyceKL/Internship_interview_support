from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_tenant_id
from backend.core.schemas import StudentCreate, StudentOut, StudentUpdate
from backend.storage.database import get_db
from backend.storage.models import Student

router = APIRouter(prefix="/students", tags=["students"])


@router.post("", response_model=StudentOut)
def create_student(payload: StudentCreate, tenant_id: int = Depends(get_current_tenant_id), db: Session = Depends(get_db)) -> StudentOut:
    student = Student(
        tenant_id=tenant_id,
        class_id=payload.class_id,
        cohort_id=payload.cohort_id,
        full_name=payload.full_name,
        student_code=payload.student_code,
        major=payload.major,
        target_domain=payload.target_domain.value,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return StudentOut.model_validate(student, from_attributes=True)


@router.get("", response_model=list[StudentOut])
def list_students(tenant_id: int = Depends(get_current_tenant_id), db: Session = Depends(get_db)) -> list[StudentOut]:
    students = db.query(Student).filter(Student.tenant_id == tenant_id).all()
    return [StudentOut.model_validate(s, from_attributes=True) for s in students]


@router.patch("/{student_id}", response_model=StudentOut)
def update_student(student_id: int, payload: StudentUpdate, tenant_id: int = Depends(get_current_tenant_id), db: Session = Depends(get_db)) -> StudentOut:
    student = db.query(Student).filter(Student.id == student_id, Student.tenant_id == tenant_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "target_domain" and value is not None:
            setattr(student, field, value.value)
        else:
            setattr(student, field, value)
    db.commit()
    db.refresh(student)
    return StudentOut.model_validate(student, from_attributes=True)
