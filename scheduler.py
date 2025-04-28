from apscheduler.schedulers.background import BackgroundScheduler
from db import init_db, get_all_users, get_friends_with_status, update_friend_status, get_all_peer_reviews
from school21_api import fetch_user_workstation
import datetime

def start_scheduler(app):
    init_db()
    sched = BackgroundScheduler()
    # каждые 2 минуты — проверка друзей
    sched.add_job(lambda: _check_friends(app), 'interval', minutes=2)
    # каждые 10 минут — напоминания о peer-review
    sched.add_job(lambda: _check_reviews(app), 'interval', minutes=10)
    sched.start()

def _check_friends(app):
    for tg_id in get_all_users():
        friends = get_friends_with_status(tg_id)
        for fr in friends:
            data = fetch_user_workstation(fr["login"])
            current = "present" if data and data.get("clusterId") else "absent"
            if fr["last"] != current:
                text = (
                    f"🟢 Друг `{fr['login']}` пришёл в кампус!"
                    if current=="present"
                    else f"🔴 Друг `{fr['login']}` покинул кампус."
                )
                app.bot.send_message(chat_id=tg_id, text=text, parse_mode="Markdown")
                update_friend_status(fr["id"], current)

def _check_reviews(app):
    now = datetime.datetime.utcnow()
    for ev in get_all_peer_reviews():
        dt = datetime.datetime.fromisoformat(ev["date"])
        # за 5 минут до события — напоминание
        delta = (dt - now).total_seconds()
        if 0 < delta <= 300:
            app.bot.send_message(
                chat_id=ev["telegram_id"],
                text=f"⏰ Напоминание: peer-review для `{ev['login']}` в {ev['date']} UTC",
                parse_mode="Markdown"
            )
