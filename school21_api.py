import os
import requests
from datetime import datetime, timedelta

TOKEN_URL = 'https://auth.sberclass.ru/auth/realms/EduPowerKeycloak/protocol/openid-connect/token'
API_BASE_URL = 'https://edu-api.21-school.ru/services/21-school/api/v1'
CLIENT_ID = 's21-open-api'

def authenticate(login: str, password: str):
    data = {
        'grant_type': 'password',
        'client_id': CLIENT_ID,
        'username': login,
        'password': password
    }
    resp = requests.post(TOKEN_URL, data=data)
    if resp.status_code != 200:
        return None, None, None
    d = resp.json()
    access_token = d['access_token']
    refresh_token = d['refresh_token']
    expires_in = d['expires_in']
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 60)
    return access_token, refresh_token, expires_at

def refresh_access_token(refresh_token: str):
    data = {
        'grant_type': 'refresh_token',
        'client_id': CLIENT_ID,
        'refresh_token': refresh_token
    }
    resp = requests.post(TOKEN_URL, data=data)
    if resp.status_code != 200:
        return None, None, None
    d = resp.json()
    access_token = d['access_token']
    refresh_token = d['refresh_token']
    expires_in = d['expires_in']
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 60)
    return access_token, refresh_token, expires_at

def ensure_token(user_data: dict):
    if 'access_token' not in user_data:
        return False
    if datetime.utcnow() >= user_data['expires_at']:
        at, rt, exp = refresh_access_token(user_data['refresh_token'])
        if at is None:
            return False
        user_data.update({
            'access_token': at,
            'refresh_token': rt,
            'expires_at': exp
        })
    return True

def api_get(user_data: dict, path: str, params=None):
    if not ensure_token(user_data):
        return None, 'auth_error'
    headers = {'Authorization': f"Bearer {user_data['access_token']}"}
    url = f"{API_BASE_URL}{path}"
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code == 401:
        # попробуем обновить и повторить
        if ensure_token(user_data):
            headers['Authorization'] = f"Bearer {user_data['access_token']}"
            resp = requests.get(url, headers=headers, params=params)
    return resp, None
