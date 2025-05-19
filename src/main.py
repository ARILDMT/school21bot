import os
import sys
import asyncio
from flask import Flask, send_from_directory, request, Response, jsonify, Blueprint
from telegram import Update
import requests
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models import db, User, init_db
from src.telegram_bot import setup_telegram_bot, BOT_TOKEN
from src.s21_routes import s21_data_bp
from src.peer_review_routes import pr_bp

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

    try:
        response = requests.post(SCHOOL21_TOKEN_URL, data=payload)
        response.raise_for_status()
        token_data = response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Auth failed", "details": str(e)}), 500

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

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"))
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev_key")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', '')}"
    f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 's21_peerconnect_db')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

init_db(app)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
setup_telegram_bot(app)
telegram_bot_app = app.extensions["telegram_bot_app"]

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
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
