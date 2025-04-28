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

# Старт /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Привет!\n\n"
        "Этот бот был разработан для студентов Школы 21, чтобы отслеживать XP, друзей в кампусе и прогресс по проектам.\n\n"
        "Авторы:\n"
        "Дима — TG: @OdintD | sh21: whirlpon\n"
        "Арси — TG: @arildmt | sh21: fernaani\n\n"
        "Введите /register <логин> чтобы зарегистрироваться.\n\n"
        "📋 Команды:\n"
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

# Регистрация /register
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Введите логин: /register <логин>")
        return
    login = context.args[0]
    telegram_id = update.effective_user.id
    username = update.effective_user.username or "unknown"

    code = ''.join(random.choices(string.digits, k=6))
    success = send_code_to_user(login, code)

    if success:
        add_user(telegram_id, username, code, login)
        await update.message.reply_text("Код подтверждения отправлен через Rocket.Chat! Введите его командой /confirm <код>")
    else:
        await update.message.reply_text("Не удалось отправить код через Rocket.Chat.")

# Подтверждение /confirm
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Введите код: /confirm <код>")
        return
    entered_code = context.args[0]
    user = get_user_by_telegram_id(update.effective_user.id)

    if user and user[3] == entered_code:
        update_registration_status(update.effective_user.id)
        await update.message.reply_text("Вы успешно зарегистрированы!")
    else:
        await update.message.reply_text("Неверный код. Попробуйте снова.")

# Команда /check [логин]
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = context.args[0] if context.args else None
    if not login:
        user = get_user_by_telegram_id(update.effective_user.id)
        if not user or not user[5]:
            await update.message.reply_text("Сначала зарегистрируйтесь через /register.")
            return
        login = user[5]

    url = f"{API_BASE_URL}/clusters/peer/{login}"
    headers = {"Authorization": SCHOOL_API_TOKEN}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        await update.message.reply_text(
            f"{login} находится в кампусе {data['clusterName']}, ряд {data['row']}, место {data['number']}."
        )
    else:
        await update.message.reply_text(f"Не удалось получить информацию о {login}.")

# Команда /checkall
async def checkall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_by_telegram_id(update.effective_user.id)
    if not user or user[4] == 0:
        await update.message.reply_text("Сначала зарегистрируйтесь через /register.")
        return

    friends = list_friends(update.effective_user.id)
    if not friends:
        await update.message.reply_text("У вас пока нет друзей. Добавьте через /addfriend <логин>.")
        return

    headers = {"Authorization": SCHOOL_API_TOKEN}
    results = []
    for login in friends:
        url = f"{API_BASE_URL}/clusters/peer/{login}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            results.append(f"{login}: {data['clusterName']}, ряд {data['row']}, место {data['number']}")
        else:
            results.append(f"{login}: Не найден")

    await update.message.reply_text("\n".join(results))

# Команда /myxp
async def myxp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_by_telegram_id(update.effective_user.id)
    if not user:
        await update.message.reply_text("Сначала зарегистрируйтесь через /register.")
        return

    login = user[5]
    url = f"{API_BASE_URL}/peers/{login}/xp"
    headers = {"Authorization": SCHOOL_API_TOKEN}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        total_xp = sum(item['amount'] for item in data)
        await update.message.reply_text(f"Ваш суммарный XP: {total_xp}")
    else:
        await update.message.reply_text("Не удалось получить XP.")

# Команда /mylevel
async def mylevel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_by_telegram_id(update.effective_user.id)
    if not user:
        await update.message.reply_text("Сначала зарегистрируйтесь через /register.")
        return

    login = user[5]
    url = f"{API_BASE_URL}/peers/{login}"
    headers = {"Authorization": SCHOOL_API_TOKEN}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        await update.message.reply_text(f"Ваш уровень: {data['level']:.2f}")
    else:
        await update.message.reply_text("Не удалось получить уровень.")

# Команда /myprojects
async def myprojects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_by_telegram_id(update.effective_user.id)
    if not user:
        await update.message.reply_text("Сначала зарегистрируйтесь через /register.")
        return

    login = user[5]
    url = f"{API_BASE_URL}/peers/{login}/projects"
    headers = {"Authorization": SCHOOL_API_TOKEN}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        projects = response.json()
        text = "\n".join([f"{p['title']} - {p['status']}" for p in projects])
        await update.message.reply_text(text)
    else:
        await update.message.reply_text("Не удалось получить проекты.")

# Команда /myskills
async def myskills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_by_telegram_id(update.effective_user.id)
    if not user:
        await update.message.reply_text("Сначала зарегистрируйтесь через /register.")
        return

    login = user[5]
    url = f"{API_BASE_URL}/peers/{login}/skills"
    headers = {"Authorization": SCHOOL_API_TOKEN}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        skills = response.json()
        text = "\n".join([f"{s['name']}: {s['points']}" for s in skills])
        await update.message.reply_text(text)
    else:
        await update.message.reply_text("Не удалось получить навыки.")

# Команда /mybadges
async def mybadges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_by_telegram_id(update.effective_user.id)
    if not user:
        await update.message.reply_text("Сначала зарегистрируйтесь через /register.")
        return

    login = user[5]
    url = f"{API_BASE_URL}/peers/{login}/badges"
    headers = {"Authorization": SCHOOL_API_TOKEN}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        badges = response.json()
        text = "\n".join([f"{b['name']}" for b in badges])
        await update.message.reply_text(text)
    else:
        await update.message.reply_text("Не удалось получить значки.")

# Команда /logtime
async def logtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_by_telegram_id(update.effective_user.id)
    if not user:
        await update.message.reply_text("Сначала зарегистрируйтесь через /register.")
        return

    login = user[5]
    url = f"{API_BASE_URL}/peers/{login}/locations-stats"
    headers = {"Authorization": SCHOOL_API_TOKEN}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        average = data.get("averageTime")
        await update.message.reply_text(f"Среднее время в кампусе: {average} минут в день.")
    else:
        await update.message.reply_text("Не удалось получить статистику.")

# Добавить друга /addfriend
async def addfriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Введите логин друга: /addfriend <логин>")
        return
    friend_login = context.args[0]
    add_friend(update.effective_user.id, friend_login)
    await update.message.reply_text(f"Друг {friend_login} добавлен!")

# Удалить друга /removefriend
async def removefriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Введите логин друга: /removefriend <логин>")
        return
    friend_login = context.args[0]
    remove_friend(update.effective_user.id, friend_login)
    await update.message.reply_text(f"Друг {friend_login} удалён.")

# Список друзей /listfriends
async def listfriends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    friends = list_friends(update.effective_user.id)
    if friends:
        await update.message.reply_text("Ваши друзья:\n" + "\n".join(friends))
    else:
        await update.message.reply_text("У вас нет друзей.")
