from __future__ import annotations

import json
import logging

import streamlit as st
from dotenv import load_dotenv

from exports.report_exporter import build_docx_report, build_markdown_report
from parsers.cv_parser import parse_cv_file
from services.qa_service import generate_interview_qa
from services.review_service import build_cv_review
from storage.db import init_db, list_history, save_analysis
from ui.components import sidebar_inputs

load_dotenv()
logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="Internship Interview Support", layout="wide")
init_db()

st.title("Internship CV Review & Interview Q&A MVP")

inputs = sidebar_inputs()

with st.form("lecturer_form"):
    c1, c2, c3 = st.columns(3)
    student_name = c1.text_input("Tên sinh viên")
    student_id = c2.text_input("Mã sinh viên")
    major = c3.text_input("Ngành học")
    lecturer_notes = st.text_area("Ghi chú thủ công của giảng viên")
    analyze_clicked = st.form_submit_button("Analyze CV")

if "cv_review" not in st.session_state:
    st.session_state.cv_review = None
if "qa" not in st.session_state:
    st.session_state.qa = None

if analyze_clicked:
    if not inputs["uploaded"]:
        st.error("Vui lòng upload CV.")
    else:
        parsed = parse_cv_file(inputs["uploaded"].name, inputs["uploaded"].read())
        parsed.student_info.name = student_name or parsed.student_info.name
        parsed.student_info.student_id = student_id
        parsed.student_info.major = major

        review = build_cv_review(parsed, inputs["role"], inputs["language"], inputs["jd_text"], lecturer_notes)
        qa = generate_interview_qa(parsed, inputs["role"], inputs["language"], inputs["qa_mode"])

        st.session_state.cv_review = review.model_dump()
        st.session_state.qa = qa.model_dump()

        save_analysis(
            {
                "student_name": parsed.student_info.name,
                "student_id": student_id,
                "major": major,
                "target_role": inputs["role"],
                "language": inputs["language"],
                "cv_review": st.session_state.cv_review,
                "qa": st.session_state.qa,
                "lecturer_notes": lecturer_notes,
            }
        )
        st.success("Phân tích hoàn tất.")

tab1, tab2, tab3, tab4 = st.tabs(["CV Review", "Interview Q&A", "History", "Settings"])

with tab1:
    if st.session_state.cv_review:
        st.json(st.session_state.cv_review)
    else:
        st.info("Chưa có dữ liệu CV review.")

with tab2:
    if st.session_state.qa:
        st.json(st.session_state.qa)
    else:
        st.info("Chưa có dữ liệu interview Q&A.")

with tab3:
    rows = list_history()
    if rows:
        for row in rows:
            st.markdown(f"### #{row['id']} - {row['student_name']} - {row['created_at']}")
            st.code(json.dumps(row, ensure_ascii=False, indent=2), language="json")
    else:
        st.info("Chưa có lịch sử.")

with tab4:
    st.write("Xuất báo cáo nếu đã có dữ liệu.")
    if st.session_state.cv_review and st.session_state.qa:
        md_content = build_markdown_report(st.session_state.cv_review, st.session_state.qa, audience="lecturer")
        docx_content = build_docx_report(st.session_state.cv_review, st.session_state.qa, audience="student")
        st.download_button("Export Report (Markdown)", data=md_content, file_name="report.md")
        st.download_button(
            "Export Report (DOCX)",
            data=docx_content,
            file_name="report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
