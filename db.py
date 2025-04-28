import os
import sqlite3
from threading import Lock

DB_PATH = os.getenv("DATABASE_URL", "bot.db")
_lock = Lock()

def _get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    with _lock, _get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id    INTEGER PRIMARY KEY,
                username       TEXT,
                confirmation_code TEXT,
                login          TEXT,
                registered     INTEGER DEFAULT 0
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS friends (
                telegram_id    INTEGER,
                friend_login   TEXT,
                PRIMARY KEY(telegram_id, friend_login)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS friend_status (
                telegram_id    INTEGER,
                friend_login   TEXT,
                in_campus      INTEGER DEFAULT 0,
                PRIMARY KEY(telegram_id, friend_login)
            )
        """)
        conn.commit()

def add_user(tg_id, username, code, login):
    with _lock, _get_conn() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO users
            (telegram_id, username, confirmation_code, login, registered)
            VALUES (?, ?, ?, ?, 0)
        """, (tg_id, username, code, login))
        conn.commit()

def get_user_by_telegram_id(tg_id):
    with _lock, _get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE telegram_id = ?", (tg_id,)).fetchone()
        return row

def update_registration_status(tg_id):
    with _lock, _get_conn() as conn:
        conn.execute("UPDATE users SET registered = 1 WHERE telegram_id = ?", (tg_id,))
        conn.commit()

def add_friend(tg_id, friend_login):
    with _lock, _get_conn() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO friends (telegram_id, friend_login)
            VALUES (?, ?)
        """, (tg_id, friend_login))
        conn.commit()

def remove_friend(tg_id, friend_login):
    with _lock, _get_conn() as conn:
        conn.execute("""
            DELETE FROM friends
            WHERE telegram_id = ? AND friend_login = ?
        """, (tg_id, friend_login))
        conn.commit()
        # also cleanup status
        conn.execute("""
            DELETE FROM friend_status
            WHERE telegram_id = ? AND friend_login = ?
        """, (tg_id, friend_login))
        conn.commit()

def list_friends(tg_id):
    with _lock, _get_conn() as conn:
        rows = conn.execute("""
            SELECT friend_login FROM friends
            WHERE telegram_id = ?
        """, (tg_id,)).fetchall()
        return [r["friend_login"] for r in rows]

def get_all_users():
    with _lock, _get_conn() as conn:
        rows = conn.execute("""
            SELECT telegram_id FROM users
            WHERE registered = 1
        """).fetchall()
        return [r["telegram_id"] for r in rows]

def get_friend_status(tg_id, friend_login):
    with _lock, _get_conn() as conn:
        row = conn.execute("""
            SELECT in_campus FROM friend_status
            WHERE telegram_id = ? AND friend_login = ?
        """, (tg_id, friend_login)).fetchone()
        return row["in_campus"] if row else 0

def set_friend_status(tg_id, friend_login, in_campus):
    with _lock, _get_conn() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO friend_status
            (telegram_id, friend_login, in_campus)
            VALUES (?, ?, ?)
        """, (tg_id, friend_login, in_campus))
        conn.commit()
