import sqlite3
import uuid
import json
from datetime import datetime
from pathlib import Path
from enum import Enum

DB_PATH = Path("jobs.db")


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL DEFAULT 'queued',
                character_json TEXT,
                shots_json TEXT,
                episode_name TEXT,
                result_url TEXT,
                error TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                pod_id TEXT
            )
        """)
        conn.commit()


def create_job(character_json: dict, shots_json: dict, episode_name: str = "") -> str:
    job_id = str(uuid.uuid4())[:8]
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO jobs (id, status, character_json, shots_json, episode_name, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (job_id, JobStatus.QUEUED, json.dumps(character_json), json.dumps(shots_json), episode_name, now, now)
        )
        conn.commit()
    return job_id


def update_job(job_id: str, **kwargs):
    kwargs["updated_at"] = datetime.utcnow().isoformat()
    fields = ", ".join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [job_id]
    with get_conn() as conn:
        conn.execute(f"UPDATE jobs SET {fields} WHERE id = ?", values)
        conn.commit()


def get_job(job_id: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return dict(row) if row else None


def list_jobs(limit: int = 20) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]
