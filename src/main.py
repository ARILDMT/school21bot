import os
import sys
import asyncio
import requests
from datetime import datetime, timedelta
from flask import Flask, send_from_directory, request, Response, jsonify, Blueprint
from telegram import Update

# --- Path fix ---
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models import db, User, init_db
from src.telegram_bot import setup_telegram_bot, BOT_TOKEN
from src.s21_routes import s21_data_bp
from src.peer_review_routes import pr_bp

# --- Auth Blueprint --- #
auth_bp = Blueprint("auth_bp", __name__)
SCHOOL21_TOKEN_URL = "https://auth.sberclass.ru/auth/realms/EduPowerKeycloak/protocol/openid-connect/token"
SCHOOL21_CLIENT_ID = "s21-open-api"

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    telegram_id = data.get("telegram_id")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    payload = {
        "client_id": SCHOOL21_CLIENT_ID,
        "grant_type": "password",
        "username": username,
        "password": password
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(SCHOOL21_TOKEN_URL, data=payload, headers=headers)
        response.raise_for_status()
        token_data = response.json()
    except requests.exceptions.RequestException as e:
        status_code = e.response.status_code if e.response else 500
        error_message = str(e)
        if e.response:
            try:
                error_details = e.response.json()
                error_message = error_details.get("error_description", error_message)
            except ValueError:
                pass
        return jsonify({"error": "Failed to authenticate", "details": error_message}), status_code

    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in", 3600)

    user = User.query.filter_by(school21_login=username).first()
    if not user:
        user = User(school21_login=username)
        db.session.add(user)

    if telegram_id:
        user.telegram_id = telegram_id

    user.set_refresh_token(refresh_token)
    user.access_token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    db.session.commit()

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "expires_in": expires_in,
        "user_school21_login": user.school21_login
    }), 200

# --- Flask App Configuration --- #
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"))
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "default_super_secret_key_for_dev")

# --- SQLite Instead of MySQL --- #
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///instance/app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

if not hasattr(app, "extensions"):
    app.extensions = {}

init_db(app)

# --- Telegram Bot ---
s_loop = asyncio.new_event_loop()
asyncio.set_event_loop(s_loop)
setup_telegram_bot(app)
telegram_bot_app = app.extensions["telegram_bot_app"]

# --- Register Blueprints ---
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(s21_data_bp, url_prefix="/s21_api")
app.register_blueprint(pr_bp, url_prefix="/api/pr")

@app.route("/telegram_webhook", methods=["POST"])
async def telegram_webhook():
    if request.method == "POST":
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, telegram_bot_app.bot)
        await telegram_bot_app.process_update(update)
        return Response(status=200)
    return "Method Not Allowed", 405

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404
    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    index_path = os.path.join(static_folder_path, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(static_folder_path, "index.html")

    encryption_key_display = "NOT_SET"
    if "ENCRYPTION_KEY_FROM_MODELS" in app.extensions:
        encryption_key_display = app.extensions["ENCRYPTION_KEY_FROM_MODELS"]
    elif hasattr(app, "newly_generated_encryption_key"):
        encryption_key_display = app.newly_generated_encryption_key + " (Newly Generated - Check Logs)"

    return f"<html><head><title>S21 PeerConnect</title></head><body><h1>Backend is running</h1><p>SQLite DB in use. Encryption key: {encryption_key_display}</p></body></html>", 200

if __name__ == "__main__":
    from src.models import ENCRYPTION_KEY as models_encryption_key
    if "Newly Generated" in models_encryption_key:
        app.newly_generated_encryption_key = models_encryption_key
    app.extensions["ENCRYPTION_KEY_FROM_MODELS"] = models_encryption_key

    print("Flask app is starting...")
    app.run(host="0.0.0.0", port=5000, debug=True)
