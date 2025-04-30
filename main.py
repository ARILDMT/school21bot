import os
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from commands import (
    start,
    auth,
    confirm,
    check,
    myxp,
    mylevel,
    myprojects,
    mybadges,
    myskills,
    logtime,
    addfriend,
    removefriend,
    listfriends,
    checkall,
)

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", "8080"))

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ── Основные команды ───────────────────────────────────────────────────────
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("auth", auth))
    app.add_handler(CommandHandler("confirm", confirm))

    # ── School21 команды ───────────────────────────────────────────────────────
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("myxp", myxp))
    app.add_handler(CommandHandler("mylevel", mylevel))
    app.add_handler(CommandHandler("myprojects", myprojects))
    app.add_handler(CommandHandler("mybadges", mybadges))
    app.add_handler(CommandHandler("myskills", myskills))
    app.add_handler(CommandHandler("logtime", logtime))
    app.add_handler(CommandHandler("addfriend", addfriend))
    app.add_handler(CommandHandler("removefriend", removefriend))
    app.add_handler(CommandHandler("listfriends", listfriends))
    app.add_handler(CommandHandler("checkall", checkall))

    # ── Запуск polling ────────────────────────────────────────────────────────
    app.run_polling()
