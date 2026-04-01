# Internship Interview Support

Repo này giữ **V1 Streamlit** và triển khai **V2 FastAPI**. Ver2 ưu tiên local UX: clone -> cấu hình `.env` -> `docker compose up -d` -> migrate -> dùng API ngay.

## Phase 1 — Audit nhanh V1/V2 hiện tại

### Current architecture
- `backend/`: FastAPI REST API (auth, students, cv, interview, analytics, exports).
- `backend/storage`: SQLAlchemy models + Alembic migrations + seed.
- `backend/integrations/openai/adapter.py`: OpenAI Responses API + structured JSON schema validation + retry.
- `backend/prompts/domains/*.json`: FE/BE/DA/QA/BA/AI config-driven rubric/checklist/keywords/interview focus.
- `app.py`, `services/*`, `parsers/*`: V1 Streamlit + business logic cũ (fallback / backward compatibility).

### Reuse được
- V1 parser/scoring/review/export vẫn tái sử dụng làm deterministic fallback khi OpenAI unavailable.
- V2 API + models + migrations + tests đã có nền tảng tốt.
- Domain configs đã có đủ 6 domain.

### Cần refactor / chuẩn hóa thêm
- Local run trước đây chưa rõ flow docker + migrate + seed.
- Thiếu preflight scripts rõ ràng cho bash/PowerShell.
- Một số bug test (password hashing backend, schema type legacy).

### Technical debt
- Analytics monthly trend đang dùng `strftime` (được cho SQLite; production PostgreSQL nên chuyển `date_trunc`).
- Chưa có object storage abstraction (hiện local filesystem theo yêu cầu).

### Migration risks
- Khác biệt SQLite vs PostgreSQL query function (đặc biệt analytics time aggregation).
- Nếu thiếu `OPENAI_API_KEY`, pipeline chuyển fallback deterministic (không fail toàn flow).

## Phase 2+ — Migration plan Ver2
1. **Stabilize local runtime**: `.env.example`, Dockerfile, compose, Makefile, preflight.
2. **Backend API hardening**: auth/tenant guards, endpoint contracts, schema validation.
3. **DB & migrations**: PostgreSQL schema, versioning CV/review/interview, seed/demo.
4. **OpenAI pipeline**: Responses API + Structured Outputs + retry + fallback.
5. **Domain-specific improvements**: FE/BE/DA/QA/BA/AI config-driven context.
6. **Analytics & exports**: dashboard APIs + markdown/docx export.
7. **Tests + e2e**: auth, tenant isolation, CRUD, schema validation, analytics, export.

## Folder structure Ver2 (đang dùng)

```text
backend/
  api/
  core/
  auth/
  tenants/
  users/                # lecturer endpoints
  students/
  cv/
  interviews/
  analytics/
  integrations/openai/
  storage/
  exports/
  prompts/domains/
  alembic/
  tests/
app/                    # compatibility namespace
data/
  uploads/cv/
  uploads/jd/
  exports/
scripts/
```

---

## How to run locally after clone (ngắn gọn)
1. `git clone <repo>`
2. `cp .env.example .env`
3. Điền `OPENAI_API_KEY` trong `.env`
4. `docker compose up -d`
5. `make migrate-docker`
6. `make seed-docker` (optional)
7. Mở `http://localhost:8000/docs`

---

## Local setup chi tiết

### 1) Clone + env
```bash
git clone <repo-url>
cd Internship_interview_support
cp .env.example .env
```

### 2) Sửa `.env`
Bắt buộc:
- `OPENAI_API_KEY=<your_key>` (nếu bỏ trống, hệ thống dùng fallback deterministic)
- giữ `DATABASE_URL` mặc định khi chạy docker compose.

### 3) Preflight
**bash**
```bash
make preflight
```

**Windows PowerShell**
```powershell
.\scripts\preflight.ps1
```

### 4) Start services
```bash
docker compose up -d --build
```

### 5) Migrate database
```bash
make migrate-docker
```

### 6) Seed demo data (optional)
```bash
make seed-docker
```

### 7) Verify health/docs
- Health: `http://localhost:8000/health`
- Swagger: `http://localhost:8000/docs`

Quick check:
```bash
curl http://localhost:8000/health
```

Expected:
```json
{"status":"ok"}
```

## API chính
- `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/me`
- `/students`
- `/cv/upload`, `/cv/parse`, `/cv/review`
- `/interview/generate`
- `/analytics/summary`, `/analytics/distribution`, `/analytics/issues`, `/analytics/trends`
- `/exports/{cv_id}/markdown`, `/exports/{cv_id}/docx`
- `/health`

## Storage local
- `./data/uploads/cv`
- `./data/uploads/jd`
- `./data/exports`

DB chỉ lưu metadata/path file.

## Testing
```bash
make test
```

## Troubleshooting
- **`docker compose up` fail vì port 5432 bận**: đổi mapping host port của db trong `docker-compose.yml`.
- **`/health` không lên**: kiểm tra `docker compose logs api`.
- **Migrate lỗi connect db**: chờ db healthy rồi chạy lại `make migrate-docker`.
- **Không có OPENAI key**: pipeline vẫn chạy bằng fallback (không sinh lỗi hard-fail).

## Notes
- Mọi output JSON của pipeline parse/review/interview đều đi qua Pydantic validation.
- Prompt/pipeline tuân thủ nguyên tắc: không bịa dữ liệu; thiếu dữ liệu trả `unknown` hoặc `cần bổ sung`.
