import os
import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, ContextTypes,
)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "Привет! Это бот для студентов Школы 21.\n\n"
        "Команды:\n"
        "/auth <логин> <пароль> – авторизация\n"
        "/myxp – мой XP\n"
        "/mylevel – мой уровень\n"
        "/myprojects – мои проекты\n"
        "/myskills – мои скиллы\n"
        "/check [логин] – проверить где пир\n"
        "/checkall – проверить всех друзей\n"
        "/addfriend <логин> – добавить друга\n"
        "/removefriend <логин> – удалить друга\n"
        "/listfriends – список друзей\n"
        "/view_slots – посмотреть peer review слоты\n"
        "/create_slot – создать слот (будет доработано)\n"
    )
    await update.message.reply_text(message)

def setup_telegram_bot(app):
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    app.extensions["telegram_bot_app"] = application

    async def run_bot():
        print("Running telegram bot webhook...")
        await application.initialize()
        await application.start()
        # Don't call idle() because we're using webhook
    import asyncio
    asyncio.create_task(run_bot())
