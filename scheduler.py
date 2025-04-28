import os
import requests
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Bot
from db import (
    get_all_users, list_friends,
    get_friend_status, set_friend_status
)

API_BASE_URL = "https://edu-api.21-school.ru/services/21-school/api/v1"
TOKEN = os.getenv("TELEGRAM_TOKEN")
SCHOOL_TOKEN = os.getenv("SCHOOL21_API_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _fetch_in_campus(login):
    url = f"{API_BASE_URL}/participants/{login}/workstation"
    res = requests.get(url, headers={"Authorization": SCHOOL_TOKEN})
    return res.status_code == 200

def _job():
    users = get_all_users()
    logger.info(f"Проверка друзей: {len(users)} пользователей.")
    bot = Bot(token=TOKEN)
    for tg_id in users:
        friends = list_friends(tg_id)
        for friend in friends:
            now = 1 if _fetch_in_campus(friend) else 0
            prev = get_friend_status(tg_id, friend)
            if now != prev:
                set_friend_status(tg_id, friend, now)
                if now:
                    bot.send_message(tg_id, f"Друг {friend} пришёл в кампус!")
                else:
                    bot.send_message(tg_id, f"Друг {friend} покинул кампус.")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(_job, 'interval', minutes=2, next_run_time=None)
    scheduler.start()
    logger.info("✅ Планировщик задач запущен!")
    return scheduler
