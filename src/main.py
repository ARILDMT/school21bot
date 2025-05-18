import os
import sys
import asyncio
import requests
from datetime import datetime, timedelta
from flask import Flask, send_from_directory, request, Response, jsonify, Blueprint
from telegram import Update

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models import db, User, init_db # Import db, User, and init_db
from src.telegram_bot import setup_telegram_bot, BOT_TOKEN
# Import new blueprints
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
    telegram_id = data.get("telegram_id") # Optional, for linking accounts

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    payload = {
        "client_id": SCHOOL21_CLIENT_ID,
        "grant_type": "password",
        "username": username,
        "password": password
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(SCHOOL21_TOKEN_URL, data=payload, headers=headers)
        response.raise_for_status() 
        token_data = response.json()
    except requests.exceptions.RequestException as e:
        status_code = e.response.status_code if e.response is not None else 500
        error_message = str(e)
        if e.response is not None:
            try:
                error_details = e.response.json()
                error_message = error_details.get("error_description", error_message)
            except ValueError:
                pass 
        return jsonify({"error": "Failed to authenticate with School21", "details": error_message}), status_code

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

# --- App Configuration --- #
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"))
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "default_super_secret_key_for_dev")

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:"
    f"{os.getenv('DB_PASSWORD', 'password')}@"
    f"{os.getenv('DB_HOST', 'localhost')}:"
    f"{os.getenv('DB_PORT', '3306')}/"
    f"{os.getenv('DB_NAME', 's21_peerconnect_db')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

if not hasattr(app, "extensions"):
    app.extensions = {}

init_db(app) 

s_loop = asyncio.new_event_loop()
asyncio.set_event_loop(s_loop)
setup_telegram_bot(app)
telegram_bot_app = app.extensions["telegram_bot_app"]

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(s21_data_bp, url_prefix="/s21_api") # For School21 data passthrough
app.register_blueprint(pr_bp, url_prefix="/api/pr") # For Peer Review specific APIs

@app.route("/telegram_webhook", methods=["POST"])
async def telegram_webhook():
    if request.method == "POST":
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, telegram_bot_app.bot)
        await telegram_bot_app.process_update(update)
        return Response(status=200)
    else:
        return "Method Not Allowed", 405

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404
    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, "index.html")
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, "index.html")
        else:
            # Display encryption key for debug purposes if models.py generated a new one
            encryption_key_display = "NOT_SET (or pre-set in environment)"
            if "ENCRYPTION_KEY_FROM_MODELS" in app.extensions:
                 encryption_key_display = app.extensions["ENCRYPTION_KEY_FROM_MODELS"]
            elif hasattr(app, "newly_generated_encryption_key"):
                 encryption_key_display = app.newly_generated_encryption_key + " (Newly Generated - Check Logs)"
            
            return f"<html><head><title>S21 PeerConnect</title></head><body><h1>Welcome to S21 PeerConnect</h1><p>Backend is running. Frontend under construction. DB Encryption Key for refresh_tokens: {encryption_key_display}</p></body></html>", 200

if __name__ == "__main__":
    print(f"Flask app starting. Telegram BOT_TOKEN: {BOT_TOKEN[:5]}...{BOT_TOKEN[-5:] if len(BOT_TOKEN) > 10 else ''}")
    print(f"Telegram webhook endpoint available at /telegram_webhook")
    print("Ensure your Telegram bot's webhook is set to YOUR_DEPLOYED_APP_URL/telegram_webhook")
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Store the encryption key from models.py in app extensions for display/debug if needed
    # This is just for demonstration; in production, you wouldn't expose this easily.
    from src.models import ENCRYPTION_KEY as models_encryption_key
    # Check if it was newly generated by models.py (by checking the print message)
    # This is a bit hacky for demo; better to manage this via app config or startup script.
    if "Newly Generated" in models_encryption_key: # This won't work as ENCRYPTION_KEY is the key itself
        app.newly_generated_encryption_key = models_encryption_key # Store it if it was just made
    app.extensions["ENCRYPTION_KEY_FROM_MODELS"] = models_encryption_key

    app.run(host="0.0.0.0", port=5000, debug=True)

