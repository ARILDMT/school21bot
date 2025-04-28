import os, time, requests, threading

_lock = threading.Lock()
_tokens = {"access":None, "refresh":None, "expiry":0}

AUTH_URL = os.getenv("SCHOOL21_AUTH_URL")
API_URL  = os.getenv("SCHOOL21_API_URL").rstrip("/")

def _get_token():
    with _lock:
        now = time.time()
        if _tokens["access"] and now < _tokens["expiry"] - 60:
            return _tokens["access"]
        payload = {
            "client_id": "s21-open-api",
            "username": os.getenv("SCHOOL21_LOGIN"),
            "password": os.getenv("SCHOOL21_PASSWORD"),
            "grant_type": "password"
        }
        r = requests.post(AUTH_URL, data=payload)
        r.raise_for_status()
        data = r.json()
        _tokens["access"]  = data["access_token"]
        _tokens["refresh"] = data["refresh_token"]
        _tokens["expiry"]  = now + data["expires_in"]
        return _tokens["access"]

def _refresh_token():
    with _lock:
        payload = {
            "client_id": "s21-open-api",
            "grant_type": "refresh_token",
            "refresh_token": _tokens["refresh"]
        }
        r = requests.post(AUTH_URL, data=payload)
        r.raise_for_status()
        data = r.json()
        _tokens["access"]  = data["access_token"]
        _tokens["refresh"] = data["refresh_token"]
        _tokens["expiry"]  = time.time() + data["expires_in"]
        return _tokens["access"]

def _api_get(path, params=None):
    token = _get_token()
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{API_URL}{path}", headers=headers, params=params)
    if r.status_code == 401:
        token = _refresh_token()
        headers["Authorization"] = f"Bearer {token}"
        r = requests.get(f"{API_URL}{path}", headers=headers, params=params)
    r.raise_for_status()
    return r.json()

def fetch_user_workstation(login):
    return _api_get(f"/v1/participants/{login}/workstation")

def fetch_user_xp(login):
    return _api_get(f"/v1/participants/{login}/points")

def fetch_user_level(login):
    u = _api_get(f"/v1/participants/{login}")
    return {"level": u["level"], "exp": u["expValue"]}

def fetch_user_projects(login):
    return _api_get(f"/v1/participants/{login}/projects")

def fetch_user_skills(login):
    return _api_get(f"/v1/participants/{login}/skills")

def fetch_user_badges(login):
    return _api_get(f"/v1/participants/{login}/badges")

def fetch_user_logtime(login):
    return _api_get(f"/v1/participants/{login}/logtime")
