import os
import random
import string
import requests

# временное хранилище; в проде — своя БД
_verification_storage = {}

ROCKET_URL    = os.getenv("ROCKET_CHAT_URL")
ROCKET_TOKEN  = os.getenv("ROCKET_CHAT_TOKEN")
ROCKET_USERID = os.getenv("ROCKET_CHAT_USER_ID")

def send_verification_code(login: str):
    code = "".join(random.choices(string.digits, k=6))
    _verification_storage[login] = code

    url = f"{ROCKET_URL}/api/v1/chat.postMessage"
    headers = {
        "X-Auth-Token": ROCKET_TOKEN,
        "X-User-Id": ROCKET_USERID,
        "Content-Type": "application/json"
    }
    payload = {
        "channel": f"@{login}",
        "text": f"Ваш код подтверждения для бота: *{code}*"
    }
    r = requests.post(url, json=payload, headers=headers)
    r.raise_for_status()

def validate_confirmation_code(login: str, code: str):
    expected = _verification_storage.get(login)
    if expected != code:
        return False, None
    # выдают всем один и тот же админ-токен
    admin_token = os.getenv("SCHOOL21_ADMIN_TOKEN")
    return True, admin_token
