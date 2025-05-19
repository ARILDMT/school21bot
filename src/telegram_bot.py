import os
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)
from telegram import Update

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

def setup_telegram_bot(app):
    from src.models import db, User

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Привет! Это бот S21 PeerConnect.\n"
            "Используй команду /auth для авторизации в API Школы 21."
        )

    async def mylogin(update: Update, context: ContextTypes.DEFAULT_TYPE):
        tg_id = str(update.message.from_user.id)
        user = User.query.filter_by(telegram_id=tg_id).first()
        if user:
            await update.message.reply_text(f"Ваш логин: {user.school21_login}")
        else:
            await update.message.reply_text("Вы не авторизованы. Используйте /auth.")

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("mylogin", mylogin))

    app.extensions["telegram_bot_app"] = application
