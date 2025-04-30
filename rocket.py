import os
import requests

BASE_URL  = os.getenv("ROCKET_CHAT_URL", "").rstrip("/")
BOT_TOKEN = os.getenv("ROCKET_CHAT_TOKEN", "")
USER_ID   = os.getenv("ROCKET_CHAT_USER_ID", "")

HEADERS = {
    "X-Auth-Token": BOT_TOKEN,
    "X-User-Id"   : USER_ID,
    "Content-type": "application/json"
}

def send_verification_code(login: str, tg_id: int) -> bool:
    # Здесь жёстко 123456, замените логику под свою
    code = "123456"
    payload = {
        "channel": str(tg_id),
        "text"   : f"Ваш код для School21-бота: {code}"
    }
    resp = requests.post(f"{BASE_URL}/api/v1/chat.postMessage", headers=HEADERS, json=payload, timeout=10)
    return resp.status_code == 200

def validate_confirmation_code(login: str, code: str) -> bool:
    return code == "123456"
