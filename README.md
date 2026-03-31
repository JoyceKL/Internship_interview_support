# Internship Interview Support MVP

Ứng dụng hỗ trợ giảng viên phân tích CV sinh viên thực tập và tạo bộ Interview Q&A cá nhân hóa.

## 1) Tính năng chính
- Upload CV PDF/DOCX và trích xuất thông tin chính.
- Chấm điểm CV theo rubric 0-10 từng nhóm và quy đổi tổng 0-100.
- Phân tích keyword gap giữa CV và JD.
- Sinh bộ Interview Q&A:
  - Chế độ thường: 15 câu
  - Chế độ chuyên sâu: 25 câu
- Lưu lịch sử phân tích vào SQLite.
- Export báo cáo Markdown và DOCX (lecturer/student).

## 2) Kiến trúc
- **UI**: Streamlit (`app.py`, `ui/`)
- **Parser**: `parsers/` (PDF/DOCX + heuristic section extraction)
- **Business services**: `services/` (scoring, review, Q&A, LLM wrapper)
- **Persistence**: `storage/db.py` (SQLite)
- **Export**: `exports/report_exporter.py`
- **Schema**: `models/schemas.py` (Pydantic)
- **Prompt templates**: `prompts/templates.py`

## 3) Cài đặt
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## 4) Biến môi trường
- `OPENAI_API_KEY`: API key OpenAI
- `OPENAI_MODEL`: model dùng cho giai đoạn mở rộng LLM
- `APP_DB_PATH`: file SQLite
- `LOG_LEVEL`: mức log

## 5) Chạy local
```bash
streamlit run app.py
```

## 6) Chạy test
```bash
pytest -q
```

## 7) Cấu trúc thư mục
```
.
├── app.py
├── ui/
├── parsers/
├── services/
├── prompts/
├── models/
├── storage/
├── exports/
├── tests/
├── sample_data/
├── requirements.txt
├── .env.example
└── README.md
```

## 8) Màn hình chính (mô tả)
- Sidebar: Upload CV, JD, target role, language, QA mode.
- Main tabs: CV Review, Interview Q&A, History, Settings.
- Nút chính: Analyze CV, Export Markdown/DOCX.

## 9) Giả định triển khai
- CV dạng text-selectable (không OCR).
- Scoring hiện tại là heuristic + rule-based để đảm bảo chạy ổn định.
- OpenAI client đã đóng gói sẵn để nâng cấp giai đoạn 2 (FastAPI backend).

## 10) Hướng phát triển v2
- Tách backend FastAPI (REST API + auth).
- Dùng OpenAI để tinh chỉnh parsing/review/Q&A JSON có kiểm thử chặt.
- Bổ sung multi-tenant lecturer accounts.
- Dashboard thống kê theo lớp/khóa.
- Tự động gợi ý cải tiến CV theo domain cụ thể (FE/BE/DA/QA/BA/AI).
