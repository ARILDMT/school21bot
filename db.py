import sqlite3

DB_NAME = "school21bot.db"

def connect():
    return sqlite3.connect(DB_NAME)

def create_tables():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                telegram_username TEXT,
                verification_code TEXT,
                is_verified INTEGER DEFAULT 0,
                school21_login TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS friends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_telegram_id INTEGER,
                friend_login TEXT,
                FOREIGN KEY (user_telegram_id) REFERENCES users(telegram_id)
            )
        ''')
        conn.commit()

# Добавить нового пользователя
def add_user(telegram_id, username, verification_code, school21_login):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (telegram_id, telegram_username, verification_code, school21_login)
            VALUES (?, ?, ?, ?)
        ''', (telegram_id, username, verification_code, school21_login))
        conn.commit()

# Найти пользователя по Telegram ID
def get_user_by_telegram_id(telegram_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        return cursor.fetchone()

# Обновить статус верификации
def update_registration_status(telegram_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users
            SET is_verified = 1
            WHERE telegram_id = ?
        ''', (telegram_id,))
        conn.commit()

# Найти пользователя по логину
def find_by_school21_login(login):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE school21_login = ?', (login,))
        return cursor.fetchone()

# Добавить друга
def add_friend(telegram_id, friend_login):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO friends (user_telegram_id, friend_login)
            VALUES (?, ?)
        ''', (telegram_id, friend_login))
        conn.commit()

# Удалить друга
def remove_friend(telegram_id, friend_login):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM friends
            WHERE user_telegram_id = ? AND friend_login = ?
        ''', (telegram_id, friend_login))
        conn.commit()

# Получить список друзей
def list_friends(telegram_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT friend_login FROM friends WHERE user_telegram_id = ?', (telegram_id,))
        return [row[0] for row in cursor.fetchall()]
