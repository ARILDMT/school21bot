from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet
import os
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

# Encryption key for refresh tokens. In a real app, this should be stored securely (e.g., env variable)
ENCRYPTION_KEY = os.getenv("REFRESH_TOKEN_ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    ENCRYPTION_KEY = Fernet.generate_key().decode() 
    print(f"WARNING: New REFRESH_TOKEN_ENCRYPTION_KEY generated: {ENCRYPTION_KEY}")
    print("Store this key securely as an environment variable for consistent encryption/decryption.")

cipher_suite = Fernet(ENCRYPTION_KEY.encode())

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    school21_login = db.Column(db.String(80), unique=True, nullable=False)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=True)
    encrypted_refresh_token = db.Column(db.String(512), nullable=True) 
    access_token_expires_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    # For slots created by this user (they are offering a review)
    offered_slots = db.relationship('PeerReviewSlot', foreign_keys='PeerReviewSlot.creator_user_id', backref='creator', lazy=True)
    # For slots booked by this user (they are receiving a review)
    booked_slots = db.relationship('PeerReviewSlot', foreign_keys='PeerReviewSlot.booker_user_id', backref='booker', lazy=True)

    def set_refresh_token(self, refresh_token):
        if refresh_token:
            self.encrypted_refresh_token = cipher_suite.encrypt(refresh_token.encode()).decode()
        else:
            self.encrypted_refresh_token = None

    def get_refresh_token(self):
        if self.encrypted_refresh_token:
            try:
                return cipher_suite.decrypt(self.encrypted_refresh_token.encode()).decode()
            except Exception as e:
                print(f"Error decrypting refresh token for user {self.school21_login}: {e}")
                return None
        return None

    def __repr__(self):
        return f'<User {self.school21_login}>'

class PeerReviewSlot(db.Model):
    __tablename__ = 'peer_review_slots'
    id = db.Column(db.Integer, primary_key=True)
    creator_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    booker_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Nullable until booked
    
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    project_name = db.Column(db.String(200), nullable=True) # Optional: project for review
    status = db.Column(db.String(50), default='available') # e.g., available, booked, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships to get User objects directly
    # creator = db.relationship('User', foreign_keys=[creator_user_id], backref='created_slots')
    # booker = db.relationship('User', foreign_keys=[booker_user_id], backref='booked_slots_as_booker')

    def to_dict(self):
        return {
            'id': self.id,
            'creator_user_login': self.creator.school21_login if self.creator else None,
            'booker_user_login': self.booker.school21_login if self.booker else None,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'project_name': self.project_name,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<PeerReviewSlot {self.id} by {self.creator_user_id} from {self.start_time} to {self.end_time}>'

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_telegram_id = db.Column(db.BigInteger, nullable=False) # Or link to User.id if users must be in DB
    receiver_telegram_id = db.Column(db.BigInteger, nullable=True) # For direct messages, null for group/bot messages
    message_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_bot_message = db.Column(db.Boolean, default=False)
    # For anonymization, we might not store actual telegram_id directly or use a hashed version if needed.
    # User request: "максимально анонимно для пользователя"
    # Storing telegram_id might be necessary for bot to reply or for user-specific history.
    # Consider if sender_user_id (FK to User.id) is better if all chat users are also app users.

    def to_dict(self):
        return {
            'id': self.id,
            'sender_telegram_id': str(self.sender_telegram_id), # Anonymize if needed before sending to client
            'receiver_telegram_id': str(self.receiver_telegram_id) if self.receiver_telegram_id else None,
            'message_text': self.message_text,
            'timestamp': self.timestamp.isoformat(),
            'is_bot_message': self.is_bot_message
        }

    def __repr__(self):
        return f'<ChatMessage {self.id} from {self.sender_telegram_id} at {self.timestamp}>'

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
    print("Database initialized and tables created (if they didn't exist).")

