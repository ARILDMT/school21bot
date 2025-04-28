import random
import string
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from db import (
    add_user, get_user_by_telegram_id, update_registration_status,
    find_by_school21_login, add_friend, remove_friend, list_friends
)
from rocket_chat import send_verification_code
from school21_api import (
    get_user_location, get_my_xp, get_my_level,
    get_my_projects, get_my_skills, get_my_badges,
    get_average_logtime
)

# Генерация случайного кода
def generate_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Привет!\n\n"
        "Этот бот был разработан для студентов Школы 21, чтобы отслеживать XP, друзей в кампусе и прогресс по проектам.\n\n"
        "Авторы:\n"
        "Дима — TG: @OdintD | sh21: whirlpon\n"
        "Арси — TG: @arildmt | sh21: fernaani\n\n"
        "Команды:\n"
        "/register <school21_login> — регистрация\n"
        "/confirm <код> — подтвердить код\n"
        "/check [login] — где пир\n"
        "/checkall — где все друзья\n"
        "/myxp — мой XP\n"
        "/mylevel — мой уровень\n"
        "/myprojects — мои проекты\n"
        "/myskills — мои навыки\n"
        "/mybadges — мои значки\n"
        "/logtime — среднее время\n"
        "/addfriend <login> — добавить друга\n"
        "/removefriend <login> — удалить друга\n"
        "/listfriends — список друзей"
    )
    keyboard = [
        ["/register", "/confirm", "/check", "/checkall"],
        ["/myxp", "/mylevel", "/myprojects", "/myskills"],
        ["/mybadges", "/logtime"],
        ["/addfriend", "/removefriend", "/listfriends"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(text, reply_markup=reply_markup)

# Регистрация
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    username = update.effective_user.username
    args = context.args

    if not args:
        await update.message.reply_text("Укажите логин Школы 21: /register fernaani")
        return

    school21_login = args[0]
    user = get_user_by_telegram_id(telegram_id)

    if user:
        await update.message.reply_text("Вы уже зарегистрированы или ожидаете подтверждения.")
        return

    code = generate_code()
    sent = send_verification_code(username, code)

    if sent:
        add_user(telegram_id, username, code, school21_login)
        await update.message.reply_text(
            "Код подтверждения отправлен в Rocket.Chat!\n"
            "Введите его через /confirm <код>."
        )
    else:
        await update.message.reply_text("Ошибка отправки кода. Попробуйте позже.")

# Подтверждение
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    args = context.args

    if not args:
        await update.message.reply_text("Укажите код подтверждения: /confirm 123456")
        return

    code = args[0]
    user = get_user_by_telegram_id(telegram_id)

    if not user:
        await update.message.reply_text("Вы не зарегистрированы. Используйте /register.")
        return

    if user[4] == code:
        update_registration_status(telegram_id)
        await update.message.reply_text("Регистрация подтверждена! Теперь доступны команды.")
    else:
        await update.message.reply_text("Неверный код подтверждения.")

# Проверка локации
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    login = args[0] if args else None
    if not login:
        user = get_user_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text("Сначала зарегистрируйтесь через /register.")
            return
        login = user[5]

    location = get_user_location(login)
    await update.message.reply_text(location)

# Проверка всех друзей
async def checkall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    friends = list_friends(telegram_id)

    if not friends:
        await update.message.reply_text("У вас нет добавленных друзей.")
        return

    results = []
    for friend_login in friends:
        location = get_user_location(friend_login)
        results.append(f"{friend_login}: {location}")

    await update.message.reply_text("\n".join(results))

# Мой XP
async def myxp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = get_my_xp(update.effective_user.id)
    await update.message.reply_text(result)

# Мой уровень
async def mylevel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = get_my_level(update.effective_user.id)
    await update.message.reply_text(result)

# Мои проекты
async def myprojects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = get_my_projects(update.effective_user.id)
    await update.message.reply_text(result)

# Мои навыки
async def myskills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = get_my_skills(update.effective_user.id)
    await update.message.reply_text(result)

# Мои значки
async def mybadges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = get_my_badges(update.effective_user.id)
    await update.message.reply_text(result)

# Мой логтайм
async def logtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = get_average_logtime(update.effective_user.id)
    await update.message.reply_text(result)

# Добавить друга
async def addfriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    args = context.args
    if not args:
        await update.message.reply_text("Укажите логин друга: /addfriend fernaani")
        return
    friend_login = args[0]
    add_friend(telegram_id, friend_login)
    await update.message.reply_text(f"Друг {friend_login} добавлен!")

# Удалить друга
async def removefriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    args = context.args
    if not args:
        await update.message.reply_text("Укажите логин друга: /removefriend fernaani")
        return
    friend_login = args[0]
    remove_friend(telegram_id, friend_login)
    await update.message.reply_text(f"Друг {friend_login} удалён.")

# Список друзей
async def listfriends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    friends = list_friends(telegram_id)

    if not friends:
        await update.message.reply_text("У вас нет добавленных друзей.")
    else:
        await update.message.reply_text("Ваши друзья:\n" + "\n".join(friends))
