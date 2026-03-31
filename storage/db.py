from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List

DB_PATH = os.getenv("APP_DB_PATH", "app_data.db")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            student_name TEXT,
            student_id TEXT,
            major TEXT,
            target_role TEXT,
            language TEXT,
            cv_review_json TEXT,
            qa_json TEXT,
            lecturer_notes TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_analysis(payload: Dict[str, Any]) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO analysis_history (
            created_at, student_name, student_id, major, target_role,
            language, cv_review_json, qa_json, lecturer_notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.utcnow().isoformat(),
            payload.get("student_name", ""),
            payload.get("student_id", ""),
            payload.get("major", ""),
            payload.get("target_role", ""),
            payload.get("language", ""),
            json.dumps(payload.get("cv_review", {}), ensure_ascii=False),
            json.dumps(payload.get("qa", {}), ensure_ascii=False),
            payload.get("lecturer_notes", ""),
        ),
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return int(row_id)


def list_history(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM analysis_history ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
