import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

# Берем токен из переменных окружения
API_TOKEN = os.getenv('SCHOOL21_API_TOKEN')

# Словарь для хранения логинов пользователей
user_logins = {}

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Привет!\n\n"
        "Этот бот был разработан для студентов Школы 21, чтобы отслеживать XP, друзей в кампусе и прогресс по проектам.\n\n"
        "Авторы:\n"
        "Дима — TG: @OdintD | sh21: whirlpon\n"
        "Арси — TG: @arildmt | sh21: fernaani\n"
    )

    # Клавиатура с командами
    keyboard = [
        ["/setlogin", "/check", "/checkall"],
        ["/myxp", "/mylevel"],
        ["/myprojects", "/myskills", "/mybadges"],
        ["/logtime", "/addfriend", "/removefriend", "/listfriends"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(text, reply_markup=reply_markup)

# Сохраняем логин пользователя
async def setlogin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        login = context.args[0]
        user_logins[update.effective_user.id] = login
        await update.message.reply_text(f"Ваш логин сохранен: {login}")
    else:
        await update.message.reply_text("Пожалуйста, укажите ваш логин после команды.")

# Проверка присутствия в кампусе
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        login = context.args[0]
    else:
        login = user_logins.get(update.effective_user.id)

    if not login:
        await update.message.reply_text("Сначала установите логин через /setlogin.")
        return

    url = f"https://edu-api.21-school.ru/services/21-school/api/v1/campus/{login}/location"
    headers = {"Authorization": API_TOKEN}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data.get("clusterName"):
            cluster = data["clusterName"]
            row = data["row"]
            number = data["number"]
            await update.message.reply_text(f"Кластер: {cluster}, Ряд: {row}, Место: {number}")
        else:
            await update.message.reply_text("Тебя нет в кампусе.")
    else:
        await update.message.reply_text("Не удалось получить данные о кампусе.")

# Получение XP
async def myxp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = user_logins.get(update.effective_user.id)
    if not login:
        await update.message.reply_text("Сначала установите логин через /setlogin.")
        return

    url = f"https://edu-api.21-school.ru/services/21-school/api/v1/users/{login}/xp"
    headers = {"Authorization": API_TOKEN}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        xp_data = response.json()
        xp = sum(item.get("amount", 0) for item in xp_data)
        await update.message.reply_text(f"Ваш XP: {xp}")
    else:
        await update.message.reply_text("Не удалось получить XP.")

# Получение уровня
async def mylevel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = user_logins.get(update.effective_user.id)
    if not login:
        await update.message.reply_text("Сначала установите логин через /setlogin.")
        return

    url = f"https://edu-api.21-school.ru/services/21-school/api/v1/users/{login}"
    headers = {"Authorization": API_TOKEN}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        user_info = response.json()
        level = user_info.get("level", "Неизвестно")
        await update.message.reply_text(f"Ваш уровень: {level}")
    else:
        await update.message.reply_text("Не удалось получить уровень.")

# Получение списка проектов
async def myprojects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = user_logins.get(update.effective_user.id)
    if not login:
        await update.message.reply_text("Сначала установите логин через /setlogin.")
return

    url = f"https://edu-api.21-school.ru/services/21-school/api/v1/users/{login}/projects"
    headers = {"Authorization": API_TOKEN}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        projects = response.json().get("projects", [])
        if not projects:
            await update.message.reply_text("Проекты не найдены.")
            return
        project_list = "\n".join(p.get("title", "Без названия") for p in projects)
        await update.message.reply_text(f"Ваши проекты:\n{project_list}")
    else:
        await update.message.reply_text("Не удалось получить проекты.")

# Получение навыков
async def myskills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = user_logins.get(update.effective_user.id)
    if not login:
        await update.message.reply_text("Сначала установите логин через /setlogin.")
        return

    url = f"https://edu-api.21-school.ru/services/21-school/api/v1/users/{login}/skills"
    headers = {"Authorization": API_TOKEN}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        skills = response.json().get("skills", [])
        if not skills:
            await update.message.reply_text("Навыки не найдены.")
            return
        skills_list = "\n".join(f"{skill['name']}: {skill['points']}" for skill in skills)
        await update.message.reply_text(f"Ваши навыки:\n{skills_list}")
    else:
        await update.message.reply_text("Не удалось получить навыки.")

# Логирование времени — пока заглушка
async def logtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Эта функция пока в разработке.")

# Друзья в кампусе — пока заглушка
async def addfriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Функция добавления друзей пока в разработке.")

async def removefriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Функция удаления друзей пока в разработке.")

async def listfriends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Функция списка друзей пока в разработке.")

async def checkall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Функция проверки всех друзей пока в разработке.")
