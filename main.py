import os
from telegram.ext import ApplicationBuilder, CommandHandler
from commands import (
    start, register, confirm,
    check, checkall, myxp, mylevel,
    myprojects, myskills, mybadges, logtime,
    addfriend, removefriend, listfriends
)
from db import create_tables
from scheduler import start_scheduler

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.environ.get("PORT", "8080"))

# 1) Создать/проверить БД
create_tables()

# 2) Построить приложение
app = ApplicationBuilder().token(BOT_TOKEN).build()

# 3) Зарегистрировать хендлеры
handlers = [
    ("/start", start),
    ("/register", register),
    ("/confirm", confirm),
    ("/check", check),
    ("/checkall", checkall),
    ("/myxp", myxp),
    ("/mylevel", mylevel),
    ("/myprojects", myprojects),
    ("/myskills", myskills),
    ("/mybadges", mybadges),
    ("/logtime", logtime),
    ("/addfriend", addfriend),
    ("/removefriend", removefriend),
    ("/listfriends", listfriends),
]
for cmd, fn in handlers:
    app.add_handler(CommandHandler(cmd, fn))

# 4) Запустить планировщик
start_scheduler()

# 5) Запустить Webhook
print("✅ Бот запущен!")
app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    webhook_url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/"
)
