import os
from telegram.ext import ApplicationBuilder, CommandHandler
from commands import (
    start, auth, confirm, check, checkall, addfriend, removefriend, listfriends,
    setreview, listreviews, removereview,
    myxp, mylevel, myprojects, myskills, mybadges, logtime
)
from scheduler import start_scheduler
from db import init_db

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT      = int(os.getenv("PORT", 8080))
HOSTNAME  = os.getenv("RENDER_EXTERNAL_HOSTNAME")

if __name__ == '__main__':
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    cmds = {
      "start": start, "auth": auth, "confirm": confirm,
      "check": check, "checkall": checkall,
      "addfriend": addfriend, "removefriend": removefriend, "listfriends": listfriends,
      "setreview": setreview, "listreviews": listreviews, "removereview": removereview,
      "myxp": myxp, "mylevel": mylevel, "myprojects": myprojects,
      "myskills": myskills, "mybadges": mybadges, "logtime": logtime
    }
    for name, fn in cmds.items():
        app.add_handler(CommandHandler(name, fn))

    start_scheduler(app)

    app.run_webhook(
      listen="0.0.0.0",
      port=PORT,
      webhook_url=f"https://{HOSTNAME}/"
    )
