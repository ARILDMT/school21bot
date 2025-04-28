import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "bot.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Пользователи
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
      telegram_id   INTEGER PRIMARY KEY,
      school_login  TEXT,
      rocket_code   TEXT
    )""")
    # Друзья + статус (“present”/“absent”)
    c.execute("""
    CREATE TABLE IF NOT EXISTS friends(
      id            INTEGER PRIMARY KEY AUTOINCREMENT,
      telegram_id   INTEGER,
      friend_login  TEXT,
      last_status   TEXT,
      FOREIGN KEY(telegram_id) REFERENCES users(telegram_id)
    )""")
    # Peer-review события
    c.execute("""
    CREATE TABLE IF NOT EXISTS peer_review(
      id            INTEGER PRIMARY KEY AUTOINCREMENT,
      telegram_id   INTEGER,
      peer_login    TEXT,
      review_date   TEXT,
      FOREIGN KEY(telegram_id) REFERENCES users(telegram_id)
    )""")
    conn.commit()
    conn.close()

# ——— Пользователь —————————————————————————————————————
def set_user_login(telegram_id, login):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users(telegram_id) VALUES(?)", (telegram_id,))
    c.execute("UPDATE users SET school_login=? WHERE telegram_id=?", (login, telegram_id))
    conn.commit(); conn.close()

def get_user_login(telegram_id):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT school_login FROM users WHERE telegram_id=?", (telegram_id,))
    row = c.fetchone(); conn.close()
    return row[0] if row else None

# ——— Верификация через Rocket.Chat ————————————————————
def set_pending_code(telegram_id, code):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("UPDATE users SET rocket_code=? WHERE telegram_id=?", (str(code), telegram_id))
    conn.commit(); conn.close()

def get_pending_code(telegram_id):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT rocket_code FROM users WHERE telegram_id=?", (telegram_id,))
    row = c.fetchone(); conn.close()
    return row[0] if row and row[0] else None

def clear_pending_code(telegram_id):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("UPDATE users SET rocket_code=NULL WHERE telegram_id=?", (telegram_id,))
    conn.commit(); conn.close()

# ——— Друзья ————————————————————————————————————————
def add_friend(telegram_id, friend_login):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("INSERT INTO friends(telegram_id,friend_login) VALUES(?,?)",
              (telegram_id, friend_login))
    conn.commit(); conn.close()

def remove_friend(telegram_id, friend_login):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("DELETE FROM friends WHERE telegram_id=? AND friend_login=?",
              (telegram_id, friend_login))
    conn.commit(); conn.close()

def get_friends(telegram_id):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT friend_login FROM friends WHERE telegram_id=?", (telegram_id,))
    rows = c.fetchall(); conn.close()
    return [r[0] for r in rows]

def get_friends_with_status(telegram_id):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT id, friend_login, last_status FROM friends WHERE telegram_id=?",
              (telegram_id,))
    rows = c.fetchall(); conn.close()
    return [{"id":r[0],"login":r[1],"last":r[2]} for r in rows]

def update_friend_status(friend_id, status):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("UPDATE friends SET last_status=? WHERE id=?", (status, friend_id))
    conn.commit(); conn.close()

# ——— Peer-review —————————————————————————————————————
def add_peer_review(telegram_id, peer_login, review_date):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("INSERT INTO peer_review(telegram_id,peer_login,review_date) VALUES(?,?,?)",
              (telegram_id, peer_login, review_date))
    conn.commit(); conn.close()

def get_peer_reviews(telegram_id):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT id, peer_login, review_date FROM peer_review WHERE telegram_id=?",
              (telegram_id,))
    rows = c.fetchall(); conn.close()
    return [{"id":r[0],"login":r[1],"date":r[2]} for r in rows]

def remove_peer_review(event_id):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("DELETE FROM peer_review WHERE id=?", (event_id,))
    conn.commit(); conn.close()

# ——— Утилиты общего доступа ——————————————————————————
def get_all_users():
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT telegram_id FROM users WHERE school_login IS NOT NULL")
    rows = c.fetchall(); conn.close()
    return [r[0] for r in rows]

def get_all_peer_reviews():
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT telegram_id,peer_login,review_date FROM peer_review")
    rows = c.fetchall(); conn.close()
    return [{"telegram_id":r[0],"login":r[1],"date":r[2]} for r in rows]
