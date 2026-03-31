# Internship Interview Support

Repo hiện chứa đồng thời:
- **V1 (MVP local Streamlit)** giữ nguyên để tương thích ngược.
- **V2 (production-ready foundation)** backend FastAPI tách riêng, có auth JWT, multi-tenant, analytics, OpenAI structured outputs, versioning dữ liệu CV/review/interview.

## 1) Kiến trúc Ver2

```text
backend/
  api/                      # API router tổng
  core/                     # config + shared schemas
  auth/                     # JWT, dependency authn/authz
  tenants/                  # tenant endpoints
  users/                    # lecturer endpoints
  students/                 # student CRUD
  cv/                       # upload/parse/review + versioning
  interviews/               # generate Q&A + versioning
  analytics/                # dashboard JSON endpoints
  prompts/                  # domain configs + prompt context
  integrations/openai/      # adapter structured output + retry
  storage/                  # SQLAlchemy models/session/seed
  exports/                  # markdown/docx export
  alembic/                  # migrations
  tests/                    # v2 tests
```

## 2) Chạy local

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Run API (V2)
```bash
make run-api
```
Swagger: `http://localhost:8000/docs`

### Run UI cũ (V1)
```bash
make run-ui
```

## 3) Database & Migration

- Ver2 target: PostgreSQL.
- Local test có thể dùng SQLite.

```bash
make migrate
make seed
```

## 4) Docker

```bash
docker compose up --build
```

## 5) Auth & Multi-tenant

- Register lecturer: tự tạo tenant nếu chưa có.
- Login trả access + refresh JWT.
- `tenant_id` xuyên suốt model và query scope.
- API layer dùng `get_current_user`, `get_current_tenant_id` để guard truy cập chéo tenant.

## 6) OpenAI Integration

3 tác vụ chính:
- `parse_cv_to_structured_json`
- `review_cv_against_rubric`
- `generate_interview_questions`

Cơ chế:
- Structured output theo JSON schema (Pydantic schema).
- Validate sau khi nhận output.
- Retry có kiểm soát (`OPENAI_MAX_RETRIES`).
- Nếu thất bại: fallback deterministic từ logic V1.
- Nguyên tắc chống bịa: thiếu dữ liệu => `unknown` hoặc `cần bổ sung`.

## 7) Domain-specific engine

Domain hỗ trợ: **FE, BE, DA, QA, BA, AI**.
Mỗi domain có config riêng trong `backend/prompts/domains/*.json`:
- rubric
- keyword packs
- checklist
- interview focus

## 8) Endpoint chính

- `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/me`
- `/tenants/current`
- `/lecturers`
- `/students` (POST/GET/PATCH)
- `/cv/upload`, `/cv/{cv_id}/parse`, `/cv/{cv_id}/review`
- `/interview/{cv_id}/generate`
- `/analytics/dashboard`
- `/exports/{cv_id}/markdown`, `/exports/{cv_id}/docx`
- `/health`

## 9) Test

```bash
make test
```

Bao gồm:
- auth flow
- tenant isolation
- schema validation
- export tests
- e2e flow: register -> login -> create student -> upload CV -> parse -> review -> generate Q&A -> analytics

## 10) Tích hợp frontend

- V1 Streamlit có thể gọi REST API dần thay cho gọi trực tiếp service local.
- Khuyến nghị rollout theo bước:
  1. streamlit upload + auth gọi backend.
  2. chuyển parse/review/qa sang API.
  3. chuyển lịch sử + dashboard sang API.

## 11) Lưu ý kỹ thuật

- Trong môi trường production PostgreSQL, analytics monthly trend nên dùng `date_trunc` thay cho `strftime` (TODO).
- V1 logic vẫn được tái sử dụng làm fallback để giữ khả năng chạy end-to-end ổn định.
