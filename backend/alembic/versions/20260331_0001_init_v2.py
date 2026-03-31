"""init v2 schema

Revision ID: 20260331_0001
Revises:
Create Date: 2026-03-31
"""

from alembic import op
import sqlalchemy as sa

revision = "20260331_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("tenants", sa.Column("id", sa.Integer, primary_key=True), sa.Column("name", sa.String(255), nullable=False), sa.Column("tenant_type", sa.String(100), nullable=False), sa.Column("created_at", sa.DateTime, nullable=False))
    op.create_index("ix_tenants_name", "tenants", ["name"], unique=True)

    op.create_table("lecturers", sa.Column("id", sa.Integer, primary_key=True), sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False), sa.Column("email", sa.String(255), nullable=False), sa.Column("full_name", sa.String(255), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("role", sa.String(20), nullable=False), sa.Column("is_active", sa.Boolean, nullable=False), sa.Column("created_at", sa.DateTime, nullable=False))
    op.create_index("ix_lecturers_email", "lecturers", ["email"], unique=True)

    op.create_table("classes", sa.Column("id", sa.Integer, primary_key=True), sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False), sa.Column("code", sa.String(50), nullable=False), sa.Column("name", sa.String(255), nullable=False))
    op.create_table("cohorts", sa.Column("id", sa.Integer, primary_key=True), sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False), sa.Column("year", sa.Integer, nullable=False), sa.Column("name", sa.String(100), nullable=False))

    op.create_table("students", sa.Column("id", sa.Integer, primary_key=True), sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False), sa.Column("class_id", sa.Integer, sa.ForeignKey("classes.id"), nullable=True), sa.Column("cohort_id", sa.Integer, sa.ForeignKey("cohorts.id"), nullable=True), sa.Column("full_name", sa.String(255), nullable=False), sa.Column("student_code", sa.String(50), nullable=False), sa.Column("major", sa.String(255), nullable=False), sa.Column("target_domain", sa.String(20), nullable=False), sa.Column("created_at", sa.DateTime, nullable=False))

    op.create_table("cvs", sa.Column("id", sa.Integer, primary_key=True), sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False), sa.Column("student_id", sa.Integer, sa.ForeignKey("students.id"), nullable=False), sa.Column("version", sa.Integer, nullable=False), sa.Column("file_name", sa.String(255), nullable=False), sa.Column("raw_text", sa.Text, nullable=False), sa.Column("created_by", sa.Integer, sa.ForeignKey("lecturers.id"), nullable=False), sa.Column("created_at", sa.DateTime, nullable=False))
    op.create_table("cv_parsing_results", sa.Column("id", sa.Integer, primary_key=True), sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False), sa.Column("cv_id", sa.Integer, sa.ForeignKey("cvs.id"), nullable=False), sa.Column("version", sa.Integer, nullable=False), sa.Column("parsed_json", sa.JSON, nullable=False), sa.Column("created_at", sa.DateTime, nullable=False))
    op.create_table("cv_review_results", sa.Column("id", sa.Integer, primary_key=True), sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False), sa.Column("cv_id", sa.Integer, sa.ForeignKey("cvs.id"), nullable=False), sa.Column("version", sa.Integer, nullable=False), sa.Column("review_json", sa.JSON, nullable=False), sa.Column("score", sa.Float, nullable=False), sa.Column("created_at", sa.DateTime, nullable=False))
    op.create_table("job_descriptions", sa.Column("id", sa.Integer, primary_key=True), sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False), sa.Column("title", sa.String(255), nullable=False), sa.Column("content", sa.Text, nullable=False), sa.Column("created_by", sa.Integer, sa.ForeignKey("lecturers.id"), nullable=False))
    op.create_table("interview_question_sets", sa.Column("id", sa.Integer, primary_key=True), sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False), sa.Column("cv_id", sa.Integer, sa.ForeignKey("cvs.id"), nullable=False), sa.Column("mode", sa.String(20), nullable=False), sa.Column("version", sa.Integer, nullable=False), sa.Column("result_json", sa.JSON, nullable=False), sa.Column("created_at", sa.DateTime, nullable=False))
    op.create_table("activity_logs", sa.Column("id", sa.Integer, primary_key=True), sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False), sa.Column("actor_id", sa.Integer, sa.ForeignKey("lecturers.id"), nullable=False), sa.Column("action", sa.String(100), nullable=False), sa.Column("entity_type", sa.String(100), nullable=False), sa.Column("entity_id", sa.Integer, nullable=False), sa.Column("meta", sa.JSON, nullable=False), sa.Column("created_at", sa.DateTime, nullable=False))


def downgrade() -> None:
    for table in ["activity_logs", "interview_question_sets", "job_descriptions", "cv_review_results", "cv_parsing_results", "cvs", "students", "cohorts", "classes", "lecturers", "tenants"]:
        op.drop_table(table)
