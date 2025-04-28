import os
import requests

ROCKET_CHAT_URL = os.getenv("ROCKET_CHAT_URL")
ROCKET_CHAT_USER = os.getenv("ROCKET_CHAT_USER")
ROCKET_CHAT_PASSWORD = os.getenv("ROCKET_CHAT_PASSWORD")

# Логинимся в Rocket.Chat
def login_to_rocket_chat():
    try:
        response = requests.post(
            f"{ROCKET_CHAT_URL}/api/v1/login",
            json={
                "user": ROCKET_CHAT_USER,
                "password": ROCKET_CHAT_PASSWORD
            }
        )
        if response.status_code == 200:
            data = response.json()
            return data['data']['authToken'], data['data']['userId']
        else:
            print("Ошибка логина в Rocket.Chat:", response.text)
            return None, None
    except Exception as e:
        print(f"Ошибка Rocket.Chat: {e}")
        return None, None

# Отправляем сообщение пользователю
def send_code_to_user(user_login, code):
    auth_token, user_id = login_to_rocket_chat()
    if not auth_token:
        return False

    headers = {
        "X-Auth-Token": auth_token,
        "X-User-Id": user_id,
        "Content-type": "application/json"
    }

    payload = {
        "roomId": f"@{user_login}",
        "text": f"Ваш код подтверждения для регистрации в боте: {code}"
    }

    try:
        response = requests.post(
            f"{ROCKET_CHAT_URL}/api/v1/chat.postMessage",
            headers=headers,
            json=payload
        )
        if response.status_code == 200:
            return True
        else:
            print("Ошибка отправки сообщения:", response.text)
            return False
    except Exception as e:
        print(f"Ошибка отправки Rocket.Chat: {e}")
        return False
