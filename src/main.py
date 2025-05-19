import os
import sys
import asyncio
import requests
from datetime import datetime, timedelta
from flask import Flask, send_from_directory, request, Response, jsonify, Blueprint
from telegram import Update

# Добавляем src в системный путь
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models import db, User, init_db
from src.telegram_bot import setup_telegram_bot, BOT_TOKEN
from src.s21_routes import s21_data_bp
from src.peer_review_routes import pr_bp

# === Авторизация через School 21 === #
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
        return jsonify({"error": "Username and password required"}), 400

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
        error_msg = str(e)
        try:
            error_msg = e.response.json().get("error_description", error_msg)
        except:
            pass
        return jsonify({"error": "Failed to authenticate", "details": error_msg}), 401

    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in", 3600)

    user = User.query.filter_by(school21_login=username).first()
    if not user:
        user = User(school21_login=username)
        db.session.add(user)

    user.access_token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    user.set_refresh_token(refresh_token)

    if telegram_id:
        user.telegram_id = telegram_id

    db.session.commit()

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "expires_in": expires_in,
        "user_school21_login": user.school21_login
    }), 200

# === Flask-приложение === #
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"))
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "default_dev_key")

# === Настройка БД === #
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:"
    f"{os.getenv('DB_PASSWORD', 'password')}@"
    f"{os.getenv('DB_HOST', 'localhost')}:"
    f"{os.getenv('DB_PORT', '3306')}/"
    f"{os.getenv('DB_NAME', 's21_peerconnect_db')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

init_db(app)

# === Бот Telegram === #
s_loop = asyncio.new_event_loop()
asyncio.set_event_loop(s_loop)
setup_telegram_bot(app)
telegram_bot_app = app.extensions["telegram_bot_app"]

# === Регистрация маршрутов === #
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(s21_data_bp, url_prefix="/s21_api")
app.register_blueprint(pr_bp, url_prefix="/api/pr")

@app.route("/telegram_webhook", methods=["POST"])
async def telegram_webhook():
    update_data = request.get_json(force=True)
    update = Update.de_json(update_data, telegram_bot_app.bot)
    await telegram_bot_app.process_update(update)
    return Response(status=200)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    index = os.path.join(app.static_folder, "index.html")
    if os.path.exists(index):
        return send_from_directory(app.static_folder, "index.html")

    encryption_key_display = app.extensions.get("ENCRYPTION_KEY_FROM_MODELS", "Not set")
    return f"""
    <html>
        <head><title>S21 PeerConnect</title></head>
        <body>
            <h1>Welcome to S21 PeerConnect</h1>
            <p>Backend is running. Frontend under construction.</p>
            <p>Refresh Token Encryption Key: {encryption_key_display}</p>
        </body>
    </html>
    """, 200

if __name__ == "__main__":
    from src.models import ENCRYPTION_KEY as models_encryption_key
    app.extensions["ENCRYPTION_KEY_FROM_MODELS"] = models_encryption_key
    print(f"Flask app starting. BOT: {BOT_TOKEN[:5]}...{BOT_TOKEN[-5:]}")
    print("Endpoint: /telegram_webhook")
    app.run(host="0.0.0.0", port=5000, debug=True)
