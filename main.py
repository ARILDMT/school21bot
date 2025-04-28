import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from db import create_tables
from commands import (
    start, register, confirm,
    check, checkall, myxp, mylevel, myprojects, myskills, mybadges, logtime,
    addfriend, removefriend, listfriends
)

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.environ.get('PORT', 8080))

# Обязательно создаём таблицы при старте
create_tables()

app = ApplicationBuilder().token(BOT_TOKEN).build()

# Регистрация команд
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("register", register))
app.add_handler(CommandHandler("confirm", confirm))
app.add_handler(CommandHandler("check", check))
app.add_handler(CommandHandler("checkall", checkall))
app.add_handler(CommandHandler("myxp", myxp))
app.add_handler(CommandHandler("mylevel", mylevel))
app.add_handler(CommandHandler("myprojects", myprojects))
app.add_handler(CommandHandler("myskills", myskills))
app.add_handler(CommandHandler("mybadges", mybadges))
app.add_handler(CommandHandler("logtime", logtime))
app.add_handler(CommandHandler("addfriend", addfriend))
app.add_handler(CommandHandler("removefriend", removefriend))
app.add_handler(CommandHandler("listfriends", listfriends))

# Запуск через Webhook для Render
app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    webhook_url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/"
)
