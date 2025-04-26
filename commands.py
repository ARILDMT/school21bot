import os
import requests
from telegram import Update
from telegram.ext import ContextTypes

SCHOOL21_API_TOKEN = os.getenv("SCHOOL21_API_TOKEN")

# Временное хранилище логинов и друзей
user_logins = {}
user_friends = {}

# Вспомогательная функция для запросов к API
def get_user_info(login):
    url = f"https://edu-api.21-school.ru/services/21-school/api/v1/users/{login}"
    headers = {
        "Authorization": SCHOOL21_API_TOKEN
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
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
        await update.message.reply_text("Пожалуйста, укажите свой логин после команды /setlogin.")
        return
    login = context.args[0]
    user_logins[update.effective_user.id] = login
    await update.message.reply_text(f"Логин установлен: {login}")

# Команда /check
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = user_logins.get(update.effective_user.id)
    if not login:
        await update.message.reply_text("Сначала используйте /setlogin чтобы установить логин.")
        return
    url = f"https://edu-api.21-school.ru/services/21-school/api/v1/users/{login}/locations"
    headers = {
        "Authorization": SCHOOL21_API_TOKEN
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json():
        location = response.json()[0]
        cluster_name = location.get('clusterName')
        await update.message.reply_text(f"Сейчас в кампусе: {cluster_name}")
    else:
        await update.message.reply_text("Пользователь не найден в кампусе.")

# Команда /myxp
async def myxp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = user_logins.get(update.effective_user.id)
    if not login:
        await update.message.reply_text("Сначала установите логин через /setlogin.")
        return
    user_info = get_user_info(login)
    if user_info:
        xp = user_info.get('wallet')
        await update.message.reply_text(f"Твой XP: {xp}")
    else:
        await update.message.reply_text("Не удалось получить данные.")

# Команда /mylevel
async def mylevel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = user_logins.get(update.effective_user.id)
    if not login:
        await update.message.reply_text("Сначала установите логин через /setlogin.")
        return
    user_info = get_user_info(login)
    if user_info:
        level = user_info.get('level')
        await update.message.reply_text(f"Твой уровень: {level}")
    else:
        await update.message.reply_text("Не удалось получить уровень.")

# Команда /myprojects
async def myprojects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = user_logins.get(update.effective_user.id)
    if not login:
        await update.message.reply_text("Сначала установите логин через /setlogin.")
        return
    url = f"https://edu-api.21-school.ru/services/21-school/api/v1/users/{login}/projects"
    headers = {
        "Authorization": SCHOOL21_API_TOKEN
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        projects = response.json()
        project_list = [p['title'] for p in projects]
        await update.message.reply_text("\n".join(project_list) if project_list else "Проектов пока нет.")
    else:
        await update.message.reply_text("Не удалось получить проекты.")

# Команда /mybadges
async def mybadges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = user_logins.get(update.effective_user.id)
    if not login:
        await update.message.reply_text("Сначала установите логин через /setlogin.")
        return
    url = f"https://edu-api.21-school.ru/services/21-school/api/v1/users/{login}/badges"
    headers = {
        "Authorization": SCHOOL21_API_TOKEN
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        badges = response.json()
        badge_list = [b['name'] for b in badges]
        await update.message.reply_text("\n".join(badge_list) if badge_list else "Бейджей пока нет.")
    else:
        await update.message.reply_text("Не удалось получить бейджи.")

# Команда /myskills
async def myskills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = user_logins.get(update.effective_user.id)
    if not login:
        await update.message.reply_text("Сначала установите логин через /setlogin.")
        return
    url = f"https://edu-api.21-school.ru/services/21-school/api/v1/users/{login}/skills"
    headers = {
        "Authorization": SCHOOL21_API_TOKEN
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        skills = response.json()
        skill_list = [f"{s['name']}: {s['points']}" for s in skills]
        await update.message.reply_text("\n".join(skill_list) if skill_list else "Навыков пока нет.")
    else:
        await update.message.reply_text("Не удалось получить навыки.")

# Команда /logtime
async def logtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Функция логирования времени пока в разработке.")

# Команда /addfriend
async def addfriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажите логин друга после команды /addfriend.")
        return
    friend_login = context.args[0]
    user_id = update.effective_user.id
    user_friends.setdefault(user_id, []).append(friend_login)
    await update.message.reply_text(f"Друг {friend_login} добавлен!")

# Команда /removefriend
async def removefriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажите логин друга после команды /removefriend.")
        return
    friend_login = context.args[0]
    user_id = update.effective_user.id
    if user_id in user_friends and friend_login in user_friends[user_id]:
        user_friends[user_id].remove(friend_login)
        await update.message.reply_text(f"Друг {friend_login} удалён!")
    else:
        await update.message.reply_text("Такого друга нет в списке.")

# Команда /listfriends
async def listfriends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    friends = user_friends.get(user_id, [])
    if friends:
        await update.message.reply_text("Твои друзья:\n" + "\n".join(friends))
    else:
        await update.message.reply_text("У тебя пока нет добавленных друзей.")

# Команда /checkall
async def checkall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    friends = user_friends.get(user_id, [])
    if not friends:
        await update.message.reply_text("Нет добавленных друзей.")
        return
    online_friends = []
    for friend_login in friends:
        url = f"https://edu-api.21-school.ru/services/21-school/api/v1/users/{friend_login}/locations"
        headers = {
            "Authorization": SCHOOL21_API_TOKEN
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200 and response.json():
            online_friends.append(friend_login)
    if online_friends:
        await update.message.reply_text("Сейчас в кампусе:\n" + "\n".join(online_friends))
    else:
        await update.message.reply_text("Никто из друзей сейчас не в кампусе.")
