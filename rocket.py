import os
import random
import threading
import requests

# Подтягиваем из .env или из переменных окружения
ROCKET_CHAT_URL = os.getenv("ROCKET_CHAT_URL")        # например: https://rocketchat-student.21-school.ru
ROCKET_CHAT_TOKEN = os.getenv("ROCKET_CHAT_TOKEN")    # ваш API-ключ или Personal Access Token
ROCKET_CHAT_USER_ID = os.getenv("ROCKET_CHAT_USER_ID")# userId бота в Rocket.Chat

# Заголовки для REST API Rocket.Chat
HEADERS = {
    "X-Auth-Token": ROCKET_CHAT_TOKEN,
    "X-User-Id": ROCKET_CHAT_USER_ID,
    "Content-Type": "application/json"
}

# В памяти будем хранить {telegram_user_id: код}
_codes: dict[str,str] = {}
_lock = threading.Lock()

def send_verification_code(telegram_user_id: str) -> None:
    """
    Сгенерировать одноразовый 6-значный код, сохранить его и отправить
    в Rocket.Chat в чат с roomId == telegram_user_id.
    """
    code = f"{random.randint(0, 999999):06d}"
    with _lock:
        _codes[telegram_user_id] = code

    payload = {
        "roomId": telegram_user_id,
        "text": f"Ваш проверочный код: {code}"
    }
    resp = requests.post(
        f"{ROCKET_CHAT_URL}/api/v1/chat.postMessage",
        headers=HEADERS,
        json=payload
    )
    resp.raise_for_status()

def validate_confirmation_code(telegram_user_id: str, code: str) -> bool:
    """
    Проверить, совпадает ли присланный пользователем код с сохранённым.
    Если совпало — удалить из памяти и вернуть True.
    """
    with _lock:
        expected = _codes.get(telegram_user_id)
        if expected and expected == code:
            del _codes[telegram_user_id]
            return True
    return False
