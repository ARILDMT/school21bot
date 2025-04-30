import os
import time
import requests

AUTH_URL = os.getenv("SCHOOL21_AUTH_URL")
API_URL  = os.getenv("SCHOOL21_API_URL").rstrip("/")
CLIENT_ID = "s21-open-api"

def authenticate(login: str, password: str) -> dict:
    """Получить access + refresh токены по логину/паролю."""
    resp = requests.post(
        AUTH_URL,
        headers={"Content-Type":"application/x-www-form-urlencoded"},
        data={
            "client_id": CLIENT_ID,
            "username": login,
            "password": password,
            "grant_type": "password"
        },
        timeout=10
    )
    resp.raise_for_status()
    tokens = resp.json()
    tokens['timestamp'] = time.time()
    return tokens

def refresh_token(refresh_token: str) -> dict:
    """Обновить access_token с помощью refresh_token."""
    resp = requests.post(
        AUTH_URL,
        headers={"Content-Type":"application/x-www-form-urlencoded"},
        data={
            "client_id": CLIENT_ID,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        },
        timeout=10
    )
    resp.raise_for_status()
    tokens = resp.json()
    tokens['timestamp'] = time.time()
    return tokens

def _ensure_tokens(user: dict) -> dict:
    """Проверить время жизни токена, при надобности обновить."""
    tokens = user['tokens']
    # обновлять за минуту до истечения
    if time.time() - tokens['timestamp'] > tokens['expires_in'] - 60:
        new = refresh_token(tokens['refresh_token'])
        user['tokens'] = new
        return new
    return tokens

def _headers(tokens: dict) -> dict:
    return {"Authorization": f"Bearer {tokens['access_token']}"}

def get_workstation(login: str, user: dict) -> dict:
    tokens = _ensure_tokens(user)
    h = _headers(tokens)
    r = requests.get(f"{API_URL}/v1/participants/{login}/workstation", headers=h, timeout=10)
    r.raise_for_status()
    return r.json()

def get_points(login: str, user: dict) -> dict:
    tokens = _ensure_tokens(user)
    h = _headers(tokens)
    r = requests.get(f"{API_URL}/v1/participants/{login}/points", headers=h, timeout=10)
    r.raise_for_status()
    return r.json()

def get_participant(login: str, user: dict) -> dict:
    tokens = _ensure_tokens(user)
    h = _headers(tokens)
    r = requests.get(f"{API_URL}/v1/participants/{login}", headers=h, timeout=10)
    r.raise_for_status()
    return r.json()

def get_projects(login: str, user: dict) -> dict:
    tokens = _ensure_tokens(user)
    h = _headers(tokens)
    r = requests.get(f"{API_URL}/v1/participants/{login}/projects", headers=h, timeout=10)
    r.raise_for_status()
    return r.json()

def get_skills(login: str, user: dict) -> dict:
    tokens = _ensure_tokens(user)
    h = _headers(tokens)
    r = requests.get(f"{API_URL}/v1/participants/{login}/skills", headers=h, timeout=10)
    r.raise_for_status()
    return r.json()

def get_badges(login: str, user: dict) -> dict:
    tokens = _ensure_tokens(user)
    h = _headers(tokens)
    r = requests.get(f"{API_URL}/v1/participants/{login}/badges", headers=h, timeout=10)
    r.raise_for_status()
    return r.json()

def get_logtime(login: str, user: dict) -> dict:
    tokens = _ensure_tokens(user)
    h = _headers(tokens)
    r = requests.get(f"{API_URL}/v1/participants/{login}/logtime", headers=h, timeout=10)
    r.raise_for_status()
    return r.json()
