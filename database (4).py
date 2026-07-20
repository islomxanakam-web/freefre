import sqlite3
from contextlib import contextmanager

from config import DB_PATH


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                joined_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS contents (
                content_key TEXT PRIMARY KEY,
                content_type TEXT,
                file_id TEXT,
                text TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


def user_exists(user_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        return cur.fetchone() is not None


def add_user(user_id: int, username: str, full_name: str) -> int:
    """Foydalanuvchini qo'shadi va umumiy foydalanuvchilar sonini qaytaradi."""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
            (user_id, username, full_name),
        )
        cur.execute("SELECT COUNT(*) FROM users")
        return cur.fetchone()[0]


def get_stats() -> dict:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM users WHERE date(joined_at) = date('now')")
        today = cur.fetchone()[0]
        return {"total": total, "today": today}


def get_all_user_ids() -> list:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users")
        return [row[0] for row in cur.fetchall()]


def save_content(content_key: str, content_type: str, file_id: str, text: str):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO contents (content_key, content_type, file_id, text, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(content_key) DO UPDATE SET
                content_type = excluded.content_type,
                file_id = excluded.file_id,
                text = excluded.text,
                updated_at = CURRENT_TIMESTAMP
            """,
            (content_key, content_type, file_id, text),
        )


def get_content(content_key: str):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT content_type, file_id, text FROM contents WHERE content_key = ?",
            (content_key,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {"content_type": row[0], "file_id": row[1], "text": row[2]}
