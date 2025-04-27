import os
import requests
from telegram import Update, BotCommand
from telegram.ext import ContextTypes

user_logins = {}

# Функция для запросов к API школы
def api_get(endpoint):
    token = os.getenv("SCHOOL21_API_TOKEN")
    headers = {"Authorization": token}
    url = f"https://edu-api.21-school.ru/services/21-school/api/v1/{endpoint}"

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception:
        return None

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет!\n\n"
        "Этот бот был разработан для студентов Школы 21, чтобы отслеживать XP, друзей в кампусе и прогресс по проектам.\n\n"
        "Авторы:\n"
        "Дима — TG: @OdintD | sh21: whirlpon\n"
        "Арси — TG: @arildmt | sh21: fernaani"
    )

    # Установим команды для меню бота
    commands = [
        BotCommand("start", "Описание бота"),
        BotCommand("setlogin", "Установить свой логин"),
        BotCommand("check", "Где ты находишься в кампусе"),
        BotCommand("myxp", "Твои XP"),
        BotCommand("mylevel", "Твой уровень"),
        BotCommand("myprojects", "Твои проекты"),
        BotCommand("mybadges", "Твои бейджи"),
        BotCommand("myskills", "Твои навыки"),
        BotCommand("logtime", "Твой logtime")
    ]
    await context.bot.set_my_commands(commands)

# /setlogin
async def setlogin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        login = context.args[0]
        user_logins[update.effective_user.id] = login
        await update.message.reply_text(f"Ваш логин сохранён: {login}")
    else:
        await update.message.reply_text("Пожалуйста, укажите логин после команды. Пример: /setlogin yourlogin")

# /check
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = user_logins.get(update.effective_user.id)
    if not login:
        await update.message.reply_text("Сначала установите логин через /setlogin.")
        return

    data = api_get(f"users/{login}/locations")
    if not data:
        await update.message.reply_text("Ошибка: Не удалось получить данные о местоположении.")
        return

    if isinstance(data, list) and len(data) > 0:
        location = data[0]
        cluster = location.get('clusterName', 'Неизвестно')
        row = location.get('row', '?')
        number = location.get('number', '?')
        await update.message.reply_text(f"Ты сейчас в кампусе:\nКластер: {cluster}\nРяд: {row}\nМесто: {number}")
    else:
        await update.message.reply_text("Тебя нет в кампусе.")

# /myxp
async def myxp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = user_logins.get(update.effective_user.id)
    if not login:
        await update.message.reply_text("Сначала установите логин через /setlogin.")
        return

    data = api_get(f"users/{login}")
    if not data:
        await update.message.reply_text("Не удалось получить данные.")
        return

    xp = data.get('totalXpAmount')
    if xp is not None:
        await update.message.reply_text(f"У тебя {xp} XP.")
    else:
        await update.message.reply_text("Не удалось получить XP.")

# /mylevel
async def mylevel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = user_logins.get(update.effective_user.id)
    if not login:
        await update.message.reply_text("Сначала установите логин через /setlogin.")
        return

    data = api_get(f"users/{login}")
    if not data:
        await update.message.reply_text("Не удалось получить данные.")
        return

    level = data.get('level')
    if level is not None:
        await update.message.reply_text(f"Твой уровень: {level}")
    else:
        await update.message.reply_text("Не удалось получить уровень.")

# /myprojects
async def myprojects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = user_logins.get(update.effective_user.id)
    if not login:
        await update.message.
reply_text("Сначала установите логин через /setlogin.")
        return

    data = api_get(f"users/{login}/projects")
    if not data:
        await update.message.reply_text("Не удалось получить проекты.")
        return

    if isinstance(data, dict) and 'projects' in data:
        projects = data['projects']
        text = "\n".join([f"- {p['title']} ({p['status']})" for p in projects])
        await update.message.reply_text(f"Твои проекты:\n{text}")
    else:
        await update.message.reply_text("Не удалось получить проекты.")

# /mybadges
async def mybadges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = user_logins.get(update.effective_user.id)
    if not login:
        await update.message.reply_text("Сначала установите логин через /setlogin.")
        return

    data = api_get(f"users/{login}/badges")
    if not data:
        await update.message.reply_text("Не удалось получить бейджи.")
        return

    if isinstance(data, dict) and 'badges' in data:
        badges = data['badges']
        text = "\n".join([f"- {b['title']}" for b in badges])
        await update.message.reply_text(f"Твои бейджи:\n{text}")
    else:
        await update.message.reply_text("Не удалось получить бейджи.")

# /myskills
async def myskills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = user_logins.get(update.effective_user.id)
    if not login:
        await update.message.reply_text("Сначала установите логин через /setlogin.")
        return

    data = api_get(f"users/{login}/skills")
    if not data:
        await update.message.reply_text("Не удалось получить навыки.")
        return

    if isinstance(data, dict) and 'skills' in data:
        skills = data['skills']
        text = "\n".join([f"- {s['name']}: {s['points']} pts" for s in skills])
        await update.message.reply_text(f"Твои навыки:\n{text}")
    else:
        await update.message.reply_text("Не удалось получить навыки.")

# /logtime
async def logtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = user_logins.get(update.effective_user.id)
    if not login:
        await update.message.reply_text("Сначала установите логин через /setlogin.")
        return

    data = api_get(f"users/{login}/logtime")
    if not data:
        await update.message.reply_text("Не удалось получить данные logtime.")
        return

    total_hours = data.get('totalHours')
    if total_hours is not None:
        await update.message.reply_text(f"Ты провёл {total_hours} часов в кампусе.")
    else:
        await update.message.reply_text("Не удалось получить logtime.")
