import os
from telegram.ext import ApplicationBuilder, CommandHandler
from commands import (
    start, setlogin, check, myxp, mylevel, myprojects,
    mybadges, myskills, logtime
)

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.environ.get('PORT', 8080))  # Порт для Render

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Хендлеры
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setlogin", setlogin))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("myxp", myxp))
    app.add_handler(CommandHandler("mylevel", mylevel))
    app.add_handler(CommandHandler("myprojects", myprojects))
    app.add_handler(CommandHandler("mybadges", mybadges))
    app.add_handler(CommandHandler("myskills", myskills))
    app.add_handler(CommandHandler("logtime", logtime))

    # Запуск через webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/"
    )
