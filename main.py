import os
from telegram.ext import ApplicationBuilder, CommandHandler
from commands import (
    start, auth, confirm, check, checkall,
    myxp, mylevel, myprojects, myskills,
    mybadges, logtime, addfriend, removefriend,
    listfriends
)

# ===== 1. Читаем переменные среды =====
BOT_TOKEN = os.environ['TELEGRAM_TOKEN']
PORT      = int(os.environ.get('PORT', 8080))
HOST      = '0.0.0.0'
# автоматически подставится ваш хост вида your-service.onrender.com
EXTERNAL_HOSTNAME = os.environ['RENDER_EXTERNAL_HOSTNAME']

# ===== 2. URL, по которому Telegram будет шлать обновления =====
# Для безопасности сделаем путь вида /<BOT_TOKEN>, чтобы никто не гадал
WEBHOOK_PATH = f"/{BOT_TOKEN}"
WEBHOOK_URL  = f"https://{EXTERNAL_HOSTNAME}{WEBHOOK_PATH}"

if __name__ == "__main__":
    # ===== 3. Собираем приложение и регистрируем команды =====
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",       start))
    app.add_handler(CommandHandler("auth",        auth))
    app.add_handler(CommandHandler("confirm",     confirm))
    app.add_handler(CommandHandler("check",       check))
    app.add_handler(CommandHandler("checkall",    checkall))
    app.add_handler(CommandHandler("myxp",        myxp))
    app.add_handler(CommandHandler("mylevel",     mylevel))
    app.add_handler(CommandHandler("myprojects",  myprojects))
    app.add_handler(CommandHandler("myskills",    myskills))
    app.add_handler(CommandHandler("mybadges",    mybadges))
    app.add_handler(CommandHandler("logtime",     logtime))
    app.add_handler(CommandHandler("addfriend",   addfriend))
    app.add_handler(CommandHandler("removefriend",removefriend))
    app.add_handler(CommandHandler("listfriends", listfriends))

    # ===== 4. Запускаем встроенный HTTP-сервер PTB =====
    # Он будет слушать поступающие webhook-запросы от Telegram
    app.run_webhook(
        listen=HOST,
        port=PORT,
        url_path=BOT_TOKEN,    # путь = /<BOT_TOKEN>
        webhook_url=WEBHOOK_URL
    )
