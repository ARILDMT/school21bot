import os
import base64
from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet
from datetime import datetime

db = SQLAlchemy()

# Генерация ключа шифрования, если он не задан в переменных окружения
ENCRYPTION_KEY = os.getenv("REFRESH_TOKEN_ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    print(f"WARNING: New REFRESH_TOKEN_ENCRYPTION_KEY generated: {ENCRYPTION_KEY}")
fernet = Fernet(ENCRYPTION_KEY.encode())

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.String(64), unique=True, nullable=True)
    school21_login = db.Column(db.String(64), unique=True, nullable=False)
    refresh_token_encrypted = db.Column(db.Text, nullable=True)
    access_token_expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_refresh_token(self, token):
        self.refresh_token_encrypted = fernet.encrypt(token.encode()).decode()

    def get_refresh_token(self):
        if not self.refresh_token_encrypted:
            return None
        try:
            return fernet.decrypt(self.refresh_token_encrypted.encode()).decode()
        except Exception:
            return None

class PeerReviewSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_login = db.Column(db.String(64), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    slot_type = db.Column(db.String(32), default="public")  # public/private
    booked_by = db.Column(db.String(64), nullable=True)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_login = db.Column(db.String(64), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
