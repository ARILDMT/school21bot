import os
import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)
from commands import (
    start,
    auth,
    confirm,
    check,
    checkall,
    addfriend,
    removefriend,
    listfriends,
    myxp,
    mylevel,
    myprojects,
    myskills,
    mybadges,
    logtime
)

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Чтение токена и порта из окружения
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 8080))


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Глобальный обработчик ошибок."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    if hasattr(update, "message") and update.message:
        await update.message.reply_text("🚨 Что-то пошло не так. Попробуйте чуть позже.")


def main():
    # Строим приложение
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Регистрируем команды
    app.add_handler(CommandHandler("start",        start))
    app.add_handler(CommandHandler("auth",         auth))
    app.add_handler(CommandHandler("confirm",      confirm))
    app.add_handler(CommandHandler("check",        check))
    app.add_handler(CommandHandler("checkall",     checkall))
    app.add_handler(CommandHandler("addfriend",    addfriend))
    app.add_handler(CommandHandler("removefriend", removefriend))
    app.add_handler(CommandHandler("listfriends",  listfriends))
    app.add_handler(CommandHandler("myxp",         myxp))
    app.add_handler(CommandHandler("mylevel",      mylevel))
    app.add_handler(CommandHandler("myprojects",   myprojects))
    app.add_handler(CommandHandler("myskills",     myskills))
    app.add_handler(CommandHandler("mybadges",     mybadges))
    app.add_handler(CommandHandler("logtime",      logtime))

    # Обработчик исключений
    app.add_error_handler(error_handler)

    # Запуск: если на Render — webhook, иначе polling
    if os.getenv("RENDER_EXTERNAL_HOSTNAME"):
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/"
        )
    else:
        app.run_polling()


if __name__ == "__main__":
    main()
