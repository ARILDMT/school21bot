import os
import requests

API_URL = "https://edu-api.21-school.ru/services/21-school/api"
API_TOKEN = os.getenv("SCHOOL21_API_TOKEN")
headers = {"Authorization": API_TOKEN}

def check_user_online(login):
    url = f"{API_URL}/v1/participants/{login}/workstation"
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200 and r.text:
            d = r.json()
            return f"Кластер: {d['clusterName']}, Ряд: {d['row']}, Место: {d['number']}"
        elif r.status_code == 200 and not r.text:
            return "Не в кампусе."
        elif r.status_code == 404:
            return "Пользователь не найден."
        elif r.status_code == 401:
            return "Неверный или истёкший токен."
        else:
            return f"Ошибка {r.status_code}"
    except Exception as e:
        return f"Ошибка: {str(e)}"

def get_user_xp(login):
    url = f"{API_URL}/v1/participants/{login}/xp"
    try:
        r = requests.get(url, headers=headers)
        print("XP:", r.status_code, r.text)
        if r.status_code == 200:
            data = r.json()
            total = sum(x['amount'] for x in data)
            return f"Твой XP: {total}"
        return f"Ошибка {r.status_code}"
    except Exception as e:
        return f"Ошибка: {str(e)}"

def get_user_level(login):
    url = f"{API_URL}/v1/participants/{login}"
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            return f"Твой уровень: {data['level']}"
        return f"Ошибка {r.status_code}"
    except Exception as e:
        return f"Ошибка: {str(e)}"

def get_user_projects(login):
    url = f"{API_URL}/v1/participants/{login}/projects"
    try:
        r = requests.get(url, headers=headers)
        print("Projects:", r.status_code, r.text)
        if r.status_code == 200:
            data = r.json()
            projects = data.get("projects", [])
            if not projects:
                return "Проектов не найдено."
            result = []
            for p in projects[:5]:
                name = p.get('title', '—')
                status = p.get('status', '—')
                final_mark = p.get('finalPercentage', '—')
                result.append(f"{name} — {status}, баллы: {final_mark}")
            return "\n".join(result)
        return f"Ошибка {r.status_code}"
    except Exception as e:
        return f"Ошибка: {str(e)}"

def get_user_badges(login):
    url = f"{API_URL}/v1/participants/{login}/badges"
    try:
        r = requests.get(url, headers=headers)
        print("Badges:", r.status_code, r.text)
        if r.status_code == 200:
            data = r.json()
            badges = data.get("badges", [])
            if not badges:
                return "Бейджей нет."
            return "Бейджи:\n" + "\n".join(b['name'] for b in badges)
        return f"Ошибка {r.status_code}"
    except Exception as e:
        return f"Ошибка: {str(e)}"

def get_user_skills(login):
    url = f"{API_URL}/v1/participants/{login}/skills"
    try:
        r = requests.get(url, headers=headers)
        print("Skills:", r.status_code, r.text)
        if r.status_code == 200:
            data = r.json()
            skills = data.get("skills", [])
            if not skills:
                return "Скиллов нет."
            return "\n".join(f"{s['name']}: {round(s['points'], 2)}" for s in skills)
        return f"Ошибка {r.status_code}"
    except Exception as e:
        return f"Ошибка: {str(e)}"

def get_user_logtime(login):
    url = f"{API_URL}/v1/participants/{login}/logtime"
    try:
        r = requests.get(url, headers=headers)
        print("Logtime:", r.status_code, r.text)
        if r.status_code == 200:
            data = r.json()
            if not data:
                return "Нет данных по logtime."
            total_hours = round(sum(entry["duration"] for entry in data) / 3600, 2)
            return f"Ты провёл {total_hours} часов в кампусе."
        return f"Ошибка {r.status_code}"
    except Exception as e:
        return f"Ошибка: {str(e)}"