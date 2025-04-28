from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 *Добро пожаловать в бот Школы 21!*\n\n"
        "Этот бот помогает:\n"
        "• Отслеживать XP\n"
        "• Следить за друзьями в кампусе\n"
        "• Контролировать прогресс по проектам\n\n"
        "*Авторы:*\n"
        "Дима — TG: @OdintD | sh21: whirlpon\n"
        "Арси — TG: @arildmt | sh21: fernaani\n\n"
        "*Как начать:*\n"
        "1. Введите `/auth <login> <password>` для авторизации\n"
        "2. Бот сохранит токены и обработает команды автоматически:\n"
        "   `/check [login]`, `/myxp`, `/mylevel` и другие\n"
        "3. При истечении токена `access_token` он обновится по `refresh_token`\n\n"
        "▶ *Доступные команды:*\n"
        "/start, /auth, /check, /checkall, /addfriend, /removefriend, /listfriends,\n"
        "/myxp, /mylevel, /myprojects, /myskills, /mybadges, /logtime\n\n"
        "Успехов в кодинге! 🚀"
    )

    keyboard = [
        ["/auth", "/check", "/checkall"],
        ["/myxp", "/mylevel"],
        ["/myprojects", "/myskills", "/mybadges"],
        ["/logtime", "/addfriend", "/removefriend", "/listfriends"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        text,
        reply_markup=reply_markup,
        parse_mode="Markdo
