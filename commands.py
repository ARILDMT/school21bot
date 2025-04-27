import os
import requests
from telegram import Update
from telegram.ext import ContextTypes

SCHOOL21_API_TOKEN = os.getenv("SCHOOL21_API_TOKEN")
HEADERS = {"Authorization": SCHOOL21_API_TOKEN}

# Память для логинов и друзей
user_logins = {}
user_friends = {}

# Универсальная функция запросов
def api_get(endpoint):
    url = f"https://edu-api.21-school.ru/services/21-school/api/v1/{endpoint}"
    response = requests.get(url, headers=HEADERS)
    print(f"Запрос к API: {url}")
    print(f"Ответ {response.status_code}: {response.text}")
    if response.status_code == 200:
        return response.json()
    return None

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет!\n\n"
        "Этот бот был разработан для студентов Школы 21, чтобы отслеживать XP, друзей в кампусе и прогресс по проектам.\n\n"
        "Авторы:\n"
        "Дима — TG: @OdintD | sh21: whirlpon\n"
        "Арси — TG: @arildmt | sh21: fernaani\n"
    )

# Команда /setlogin
async def setlogin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Пожалуйста, укажите свой логин после /setlogin.")
        return
    login = context.args[0]
    user_logins[update.effective_user.id] = login
    await update.message.reply_text(f"Ваш логин сохранен: {login}")

# Команда /check
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = user_logins.get(update.effective_user.id)
    if not login:
        await update.message.reply_text("Сначала используйте /setlogin.")
        return
    data = api_get(f"users/{login}/locations")
    if data and len(data) > 0:
        cluster = data[0].get('clusterName')
        await update.message.reply_text(f"Ты сейчас в кампусе: {cluster}")
    else:
        await update.message.reply_text("Тебя нет в кампусе.")

# Команда /myxp
async def myxp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = user_logins.get(update.effective_user.id)
    if not login:
        await update.message.reply_text("Сначала используйте /setlogin.")
        return
    data = api_get(f"users/{login}")
    if data:
        wallet = data.get("wallet", 0)
        await update.message.reply_text(f"Твой XP: {wallet}")
    else:
        await update.message.reply_text("Не удалось получить XP.")

# Команда /mylevel
async def mylevel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = user_logins.get(update.effective_user.id)
    if not login:
        await update.message.reply_text("Сначала используйте /setlogin.")
        return
    data = api_get(f"users/{login}")
    if data:
        level = data.get("level", 0)
        await update.message.reply_text(f"Твой уровень: {level}")
    else:
        await update.message.reply_text("Не удалось получить уровень.")

# Команда /myprojects
async def myprojects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = user_logins.get(update.effective_user.id)
    if not login:
        await update.message.reply_text("Сначала используйте /setlogin.")
        return
    data = api_get(f"users/{login}/projects")
    if data:
        project_titles = [p.get("title", "Без названия") for p in data]
        await update.message.reply_text("Твои проекты:\n" + "\n".join(project_titles))
    else:
        await update.message.reply_text("Не удалось получить проекты.")

# Команда /mybadges
async def mybadges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = user_logins.get(update.effective_user.id)
    if not login:
        await update.message.reply_text("Сначала используйте /setlogin.")
        return
    data = api_get(f"users/{login}/badges")
    if data:
        badge_names = [b.get("name", "Без названия") for b in data]
        await update.message.reply_text("Твои бейджи:\n" + "\n".join(badge_names))
    else:
        await update.message.reply_text("Не удалось получить бейджи.")

# Команда /myskills
async def myskills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = user_logins.get(update.effective_user.id)
    if not login:
        await update.message.reply_text("Сначала используйте /setlogin.")
        return
    data = api_get(f"users/{login}/skills")
    if data:
        skill_list = [f"{s['name']}: {s['points']} XP" for s in data]
        await update.message.reply_text("Твои навыки:\n" + "\n".join(skill_list))
    else:
        await update.message.reply_text("Не удалось получить навыки.")

# Команда /logtime (заглушка)
async def logtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Логирование времени пока не реализовано.")

# Команда /addfriend
async def addfriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажите логин друга после /addfriend.")
        return
    friend = context.args[0]
    user_id = update.effective_user.id
    user_friends.setdefault(user_id, []).append(friend)
    await update.message.reply_text(f"Друг {friend} добавлен в список!")

# Команда /removefriend
async def removefriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажите логин друга после /removefriend.")
        return
    friend = context.args[0]
    user_id = update.effective_user.id
    if user_id in user_friends and friend in user_friends[user_id]:
        user_friends[user_id].remove(friend)
        await update.message.reply_text(f"Друг {friend} удалён.")
    else:
        await update.message.reply_text("Такой друг не найден.")

# Команда /listfriends
async def listfriends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    friends = user_friends.get(user_id, [])
    if friends:
        await update.message.reply_text("Твои друзья:\n" + "\n".join(friends))
    else:
        await update.message.reply_text("У тебя нет друзей в списке.")

# Команда /checkall
async def checkall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    friends = user_friends.get(user_id, [])
    if not friends:
        await update.message.reply_text("Нет добавленных друзей.")
        return

    online_friends = []
    for friend in friends:
        data = api_get(f"users/{friend}/locations")
        if data and len(data) > 0:
            online_friends.append(friend)

    if online_friends:
        await update.message.reply_text("Сейчас в кампусе:\n" + "\n".join(online_friends))
    else:
        await update.message.reply_text("Никто из друзей не найден в кампусе.")
