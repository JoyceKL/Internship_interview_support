from __future__ import annotations

from fastapi import APIRouter

from backend.analytics.router import router as analytics_router
from backend.auth.router import router as auth_router
from backend.cv.router import router as cv_router
from backend.exports.router import router as exports_router
from backend.interviews.router import router as interview_router
from backend.students.router import router as students_router
from backend.tenants.router import router as tenants_router
from backend.users.router import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(tenants_router)
api_router.include_router(users_router)
api_router.include_router(students_router)
api_router.include_router(cv_router)
api_router.include_router(interview_router)
api_router.include_router(analytics_router)
api_router.include_router(exports_router)


@api_router.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
