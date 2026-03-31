from __future__ import annotations

import streamlit as st

ROLE_OPTIONS = [
    "Frontend Intern",
    "Backend Intern",
    "Fullstack Intern",
    "Data Analyst Intern",
    "QA Intern",
    "Business Analyst Intern",
    "AI/ML Intern",
]

LANG_OPTIONS = ["tiếng Việt", "tiếng Anh", "song ngữ Việt-Anh"]
QA_MODES = ["Thường", "Chuyên sâu"]


def sidebar_inputs() -> dict:
    st.sidebar.header("Input")
    uploaded = st.sidebar.file_uploader("Upload CV (PDF/DOCX)", type=["pdf", "docx"])
    jd_text = st.sidebar.text_area("Job Description (optional)", height=160)
    role = st.sidebar.selectbox("Vị trí ứng tuyển", ROLE_OPTIONS)
    language = st.sidebar.selectbox("Ngôn ngữ đầu ra", LANG_OPTIONS)
    qa_mode = st.sidebar.selectbox("Chế độ Q&A", QA_MODES)
    return {
        "uploaded": uploaded,
        "jd_text": jd_text,
        "role": role,
        "language": language,
        "qa_mode": qa_mode,
    }
