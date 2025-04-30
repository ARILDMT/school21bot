import os
import requests

# Базовый URL и токены из ENV
BASE_URL  = os.getenv("ROCKET_CHAT_URL", "").rstrip("/")
BOT_TOKEN = os.getenv("ROCKET_CHAT_TOKEN", "")
USER_ID   = os.getenv("ROCKET_CHAT_USER_ID", "")

HEADERS = {
    "X-Auth-Token": BOT_TOKEN,
    "X-User-Id"   : USER_ID,
    "Content-type": "application/json"
}

def send_verification_code(login: str, tg_id: int) -> bool:
    """
    Шлёт в Rocket.Chat личное сообщение с кодом подтверждения.
    login — логин пользователя (можно хранить, но для отправки не обязателен).
    tg_id — Telegram-chat-id, в который слать сообщение.
    """
    # TODO: тут сгенерировать и сохранить код в БД/кэше под этим login
    code = "123456"
    payload = {
        "channel": str(tg_id),
        "text"   : f"Ваш код подтверждения для School21-бота: {code}"
    }
    resp = requests.post(
        f"{BASE_URL}/api/v1/chat.postMessage",
        headers=HEADERS,
        json=payload,
        timeout=10
    )
    return resp.status_code == 200

def validate_confirmation_code(login: str, code: str) -> bool:
    """
    Проверяет, совпадает ли введённый пользователем код с ожидаемым.
    """
    # TODO: вместо жёсткого "123456" проверять сохранённый для login код
    return code == "123456"
