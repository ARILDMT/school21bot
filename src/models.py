import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet

db = SQLAlchemy()
ENCRYPTION_KEY = os.getenv("REFRESH_TOKEN_ENCRYPTION_KEY", Fernet.generate_key().decode())
fernet = Fernet(ENCRYPTION_KEY.encode())

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school21_login = db.Column(db.String(128), unique=True, nullable=False)
    telegram_id = db.Column(db.String(128), nullable=True)
    refresh_token_encrypted = db.Column(db.Text, nullable=True)
    access_token_expires_at = db.Column(db.DateTime, nullable=True)

    def set_refresh_token(self, token: str):
        self.refresh_token_encrypted = fernet.encrypt(token.encode()).decode()

    def get_refresh_token(self) -> str:
        return fernet.decrypt(self.refresh_token_encrypted.encode()).decode()

class PeerReviewSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    slot_type = db.Column(db.String(32), default="public")

    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    owner = db.relationship("User", foreign_keys=[owner_id])

    booked_by_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    booked_by = db.relationship("User", foreign_keys=[booked_by_id])

def init_db(app):
    if not os.path.exists("instance"):
        os.makedirs("instance")
    db.init_app(app)
    with app.app_context():
        db.create_all()
