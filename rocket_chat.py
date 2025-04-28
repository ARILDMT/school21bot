import requests
import os

ROCKET_CHAT_URL = os.getenv("ROCKET_CHAT_URL")  
ROCKET_CHAT_USER_ID = os.getenv("ROCKET_CHAT_USER_ID")  
ROCKET_CHAT_AUTH_TOKEN = os.getenv("ROCKET_CHAT_AUTH_TOKEN") 

def send_verification_code(username, code):
    url = f"{ROCKET_CHAT_URL}/api/v1/chat.postMessage"
    headers = {
        "X-Auth-Token": ROCKET_CHAT_AUTH_TOKEN,
        "X-User-Id": ROCKET_CHAT_USER_ID,
        "Content-type": "application/json"
    }
    data = {
        "channel": f"@{username}",
        "text": f"Ваш код подтверждения для регистрации в боте: {code}"
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        return True
    else:
        print(f"Ошибка отправки кода в Rocket.Chat: {response.text}")
        return False
