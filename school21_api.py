import os
import requests

API_URL     = os.getenv("SCHOOL21_API_URL").rstrip("/")
ADMIN_TOKEN = os.getenv("SCHOOL21_ADMIN_TOKEN")

def _headers():
    return {"Authorization": f"Bearer {ADMIN_TOKEN}"}

def get_workstation(login: str):
    r = requests.get(f"{API_URL}/v1/participants/{login}/workstation", headers=_headers())
    r.raise_for_status()
    return r.json()

def get_xp(login: str):
    r = requests.get(f"{API_URL}/v1/participants/{login}/points", headers=_headers())
    r.raise_for_status()
    return r.json()

def get_level(login: str):
    r = requests.get(f"{API_URL}/v1/participants/{login}", headers=_headers())
    r.raise_for_status()
    return r.json()

def get_projects(login: str):
    r = requests.get(f"{API_URL}/v1/participants/{login}/projects", headers=_headers())
    r.raise_for_status()
    return r.json()

def get_badges(login: str):
    r = requests.get(f"{API_URL}/v1/participants/{login}/badges", headers=_headers())
    r.raise_for_status()
    return r.json()

def get_skills(login: str):
    r = requests.get(f"{API_URL}/v1/participants/{login}/skills", headers=_headers())
    r.raise_for_status()
    return r.json()

def get_logtime(login: str):
    r = requests.get(f"{API_URL}/v1/participants/{login}/logtime", headers=_headers())
    r.raise_for_status()
    return r.json()  # возвращает {"logtimeWeeklyAvgHours": ...}
