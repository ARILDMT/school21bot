import os
import random
import string
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from db import (
    add_user, get_user_by_telegram_id, update_registration_status,
    add_friend, remove_friend, list_friends
)
from rocket_chat import send_code_to_user

SCHOOL_API_TOKEN = os.getenv("SCHOOL21_API_TOKEN")
API_BASE_URL = "https://edu-api.21-school.ru/services/21-school/api/v1"

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Привет!\n\n"
        "Этот бот был разработан для студентов Школы 21, чтобы отслеживать XP, друзей в кампусе и прогресс по проектам.\n\n"
        "Авторы:\n"
        "Дима — TG: @OdintD | sh21: whirlpon\n"
        "Арси — TG: @arildmt | sh21: fernaani\n\n"
        "Введите /register <логин> чтобы зарегистрироваться.\n\n"
        "📋 Доступные команды:\n"
        "/register <логин> — Регистрация\n"
        "/confirm <код> — Подтверждение кода\n"
        "/check [логин] — Проверить пира\n"
        "/checkall — Проверить всех друзей\n"
        "/myxp — Мой XP\n"
        "/mylevel — Мой уровень\n"
        "/myprojects — Мои проекты\n"
        "/myskills — Мои навыки\n"
        "/mybadges — Мои значки\n"
        "/logtime — Среднее время в кампусе\n"
        "/addfriend <логин> — Добавить друга\n"
        "/removefriend <логин> — Удалить друга\n"
        "/listfriends — Список друзей"
    )
    keyboard = [
        ["/register", "/confirm", "/check", "/checkall"],
        ["/myxp", "/mylevel", "/myprojects"],
        ["/myskills", "/mybadges", "/logtime"],
        ["/addfriend", "/removefriend", "/listfriends"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(text, reply_markup=reply_markup)

# /register
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Введите логин: /register <логин>")
        return
    login = context.args[0]
    tg_id = update.effective_user.id
    username = update.effective_user.username or "unknown"
    code = ''.join(random.choices(string.digits, k=6))
    if send_code_to_user(login, code):
        add_user(tg_id, username, code, login)
        await update.message.reply_text(
            "Код подтверждения отправлен через Rocket.Chat!\n"
            "Введите его командой /confirm <код>"
        )
    else:
        await update.message.reply_text("Не удалось отправить код через Rocket.Chat.")

# /confirm
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Введите код: /confirm <код>")
        return
    entered = context.args[0]
    user = get_user_by_telegram_id(update.effective_user.id)
    if user and user["confirmation_code"] == entered:
        update_registration_status(update.effective_user.id)
        await update.message.reply_text("Вы успешно зарегистрированы!")
    else:
        await update.message.reply_text("Неверный код, попробуйте снова.")

# helper to get work station (cluster) info
def _get_workstation(login):
    url = f"{API_BASE_URL}/participants/{login}/workstation"
    res = requests.get(url, headers={"Authorization": SCHOOL_API_TOKEN})
    return res

# /check
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = context.args[0] if context.args else None
    if not login:
        user = get_user_by_telegram_id(update.effective_user.id)
        if not user or user["registered"] == 0:
            await update.message.reply_text("Сначала зарегистрируйтесь через /register.")
            return
        login = user["login"]
    res = _get_workstation(login)
    if res.status_code == 200:
        data = res.json()
        await update.message.reply_text(
            f"{login} находится в кампусе {data['clusterName']}, "
            f"ряд {data['row']}, место {data['number']}."
        )
    else:
        await update.message.reply_text(f"Информация о {login} не найдена.")

# /checkall
async def checkall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not get_user_by_telegram_id(update.effective_user.id):
        await update.message.reply_text("Сначала зарегистрируйтесь через /register.")
        return
    friends = list_friends(update.effective_user.id)
    if not friends:
        await update.message.reply_text("У вас нет друзей. Добавьте через /addfriend.")
        return
    out = []
    for f in friends:
        res = _get_workstation(f)
        if res.status_code == 200:
            d = res.json()
            out.append(f"{f}: {d['clusterName']}, {d['row']}-{d['number']}")
        else:
            out.append(f"{f}: не найден")
    await update.message.reply_text("\n".join(out))

# /myxp
async def myxp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_by_telegram_id(update.effective_user.id)
    if not user or user["registered"] == 0:
        await update.message.reply_text("Сначала зарегистрируйтесь через /register.")
        return
    login = user["login"]
    url = f"{API_BASE_URL}/participants/{login}/xp"
    res = requests.get(url, headers={"Authorization": SCHOOL_API_TOKEN})
    if res.status_code == 200:
        total = sum(item["amount"] for item in res.json())
        await update.message.reply_text(f"Ваш суммарный XP: {total}")
    else:
        await update.message.reply_text("Не удалось получить XP.")

# /mylevel
async def mylevel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_by_telegram_id(update.effective_user.id)
    if not user or user["registered"] == 0:
        await update.message.reply_text("Сначала зарегистрируйтесь через /register.")
        return
    login = user["login"]
    url = f"{API_BASE_URL}/participants/{login}"
    res = requests.get(url, headers={"Authorization": SCHOOL_API_TOKEN})
    if res.status_code == 200:
        lvl = res.json().get("level")
        await update.message.reply_text(f"Ваш уровень: {lvl}")
    else:
        await update.message.reply_text("Не удалось получить уровень.")

# /myprojects
async def myprojects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_by_telegram_id(update.effective_user.id)
    if not user or user["registered"] == 0:
        await update.message.reply_text("Сначала зарегистрируйтесь через /register.")
        return
    login = user["login"]
    url = f"{API_BASE_URL}/participants/{login}/projects"
    res = requests.get(url, headers={"Authorization": SCHOOL_API_TOKEN})
    if res.status_code == 200:
        text = "\n".join(f"{p['title']} — {p['status']}" for p in res.json())
        await update.message.reply_text(text or "Проекты не найдены.")
    else:
        await update.message.reply_text("Не удалось получить проекты.")

# /myskills
async def myskills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_by_telegram_id(update.effective_user.id)
    if not user or user["registered"] == 0:
        await update.message.reply_text("Сначала зарегистрируйтесь через /register.")
        return
    login = user["login"]
    url = f"{API_BASE_URL}/participants/{login}/skills"
    res = requests.get(url, headers={"Authorization": SCHOOL_API_TOKEN})
    if res.status_code == 200:
        text = "\n".join(f"{s['name']}: {s['points']}" for s in res.json())
        await update.message.reply_text(text or "Навыки не найдены.")
    else:
        await update.message.reply_text("Не удалось получить навыки.")

# /mybadges
async def mybadges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_by_telegram_id(update.effective_user.id)
    if not user or user["registered"] == 0:
        await update.message.reply_text("Сначала зарегистрируйтесь через /register.")
        return
    login = user["login"]
    url = f"{API_BASE_URL}/participants/{login}/badges"
    res = requests.get(url, headers={"Authorization": SCHOOL_API_TOKEN})
    if res.status_code == 200:
        text = "\n".join(b["name"] for b in res.json())
        await update.message.reply_text(text or "Значки не найдены.")
    else:
        await update.message.reply_text("Не удалось получить значки.")

# /logtime
async def logtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_by_telegram_id(update.effective_user.id)
    if not user or user["registered"] == 0:
        await update.message.reply_text("Сначала зарегистрируйтесь через /register.")
        return
    login = user["login"]
    url = f"{API_BASE_URL}/participants/{login}/locations-stats"
    res = requests.get(url, headers={"Authorization": SCHOOL_API_TOKEN})
    if res.status_code == 200:
        avg = res.json().get("averageTime")
        await update.message.reply_text(f"Среднее время в кампусе: {avg} мин./день")
    else:
        await update.message.reply_text("Не удалось получить статистику.")

# /addfriend
async def addfriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Введите логин: /addfriend <логин>")
        return
    friend = context.args[0]
    add_friend(update.effective_user.id, friend)
    await update.message.reply_text(f"Друг {friend} добавлен!")

# /removefriend
async def removefriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Введите логин: /removefriend <логин>")
        return
    friend = context.args[0]
    remove_friend(update.effective_user.id, friend)
    await update.message.reply_text(f"Друг {friend} удалён.")

# /listfriends
async def listfriends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    friends = list_friends(update.effective_user.id)
    await update.message.reply_text(
        "Ваши друзья:\n" + "\n".join(friends)
        if friends else "У вас нет друзей."
    )
