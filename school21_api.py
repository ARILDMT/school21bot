import os
import requests

SCHOOL21_API_TOKEN = os.getenv("SCHOOL21_API_TOKEN")
API_BASE_URL = "https://edu-api.21-school.ru/services/21-school/api/v1"

HEADERS = {
    "Authorization": SCHOOL21_API_TOKEN
}

def get_user_location(login):
    try:
        url = f"{API_BASE_URL}/users/{login}/location"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data:
                return f"{login} находится в кластере {data['clusterName']} (ряд {data['row']}, место {data['number']})."
            else:
                return f"{login} не в кампусе."
        else:
            return f"Ошибка при проверке локации: {response.status_code}"
    except Exception as e:
        return f"Ошибка: {e}"

def get_my_xp(telegram_id):
    login = get_login_by_telegram_id(telegram_id)
    if not login:
        return "Вы не зарегистрированы."
    try:
        url = f"{API_BASE_URL}/users/{login}/xp"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            xp = response.json().get("xp", 0)
            return f"Ваш суммарный XP: {xp}"
        else:
            return "Не удалось получить XP."
    except Exception as e:
        return f"Ошибка: {e}"

def get_my_level(telegram_id):
    login = get_login_by_telegram_id(telegram_id)
    if not login:
        return "Вы не зарегистрированы."
    try:
        url = f"{API_BASE_URL}/users/{login}/level"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            level = response.json().get("level", 0)
            return f"Ваш текущий уровень: {level}"
        else:
            return "Не удалось получить уровень."
    except Exception as e:
        return f"Ошибка: {e}"

def get_my_projects(telegram_id):
    login = get_login_by_telegram_id(telegram_id)
    if not login:
        return "Вы не зарегистрированы."
    try:
        url = f"{API_BASE_URL}/projects?userLogin={login}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            projects = response.json().get("projects", [])
            if not projects:
                return "Проекты не найдены."
            return "\n".join([f"{p['title']}: {p['status']}" for p in projects])
        else:
            return "Не удалось получить проекты."
    except Exception as e:
        return f"Ошибка: {e}"

def get_my_skills(telegram_id):
    login = get_login_by_telegram_id(telegram_id)
    if not login:
        return "Вы не зарегистрированы."
    try:
        url = f"{API_BASE_URL}/skills?userLogin={login}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            skills = response.json().get("skills", [])
            if not skills:
                return "Навыки не найдены."
            return "\n".join([f"{s['name']}: {s['points']} очков" for s in skills])
        else:
            return "Не удалось получить навыки."
    except Exception as e:
        return f"Ошибка: {e}"

def get_my_badges(telegram_id):
    login = get_login_by_telegram_id(telegram_id)
    if not login:
        return "Вы не зарегистрированы."
    try:
        url = f"{API_BASE_URL}/badges?userLogin={login}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            badges = response.json().get("badges", [])
            if not badges:
                return "Нет полученных значков."
            return "\n".join([badge["name"] for badge in badges])
        else:
            return "Не удалось получить значки."
    except Exception as e:
        return f"Ошибка: {e}"

def get_average_logtime(telegram_id):
    login = get_login_by_telegram_id(telegram_id)
    if not login:
        return "Вы не зарегистрированы."
    try:
        url = f"{API_BASE_URL}/logtime/average?userLogin={login}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            hours = response.json().get("hours", 0)
            return f"Ваше среднее время в кампусе: {hours} часов."
        else:
            return "Не удалось получить данные логтайма."
    except Exception as e:
        return f"Ошибка: {e}"

# Получение логина по Telegram ID (будет через db)
from db import get_user_by_telegram_id

def get_login_by_telegram_id(telegram_id):
    user = get_user_by_telegram_id(telegram_id)
    if user:
        return user[5]  # Индекс 5 — login в базе
    return None
