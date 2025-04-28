import os
from telegram.ext import ApplicationBuilder, CommandHandler
from commands import (
    start, auth, check, checkall, myxp, mylevel, myprojects, myskills,
    mybadges, logtime, addfriend, removefriend, listfriends
)
from scheduler import start_scheduler

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.environ.get('PORT', 8080))  # Порт для Render

commands = {
    "start": start,
    "auth": auth,
    "check": check,
    "checkall": checkall,
    "myxp": myxp,
    "mylevel": mylevel,
    "myprojects": myprojects,
    "myskills": myskills,
    "mybadges": mybadges,
    "logtime": logtime,
    "addfriend": addfriend,
    "removefriend": removefriend,
    "listfriends": listfriends
}

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    for cmd, fn in commands.items():
        app.add_handler(CommandHandler(cmd, fn))

    start_scheduler(app)  # Запустить планировщик уведомлений

    # Запуск через webhook для Render
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/"
    )
