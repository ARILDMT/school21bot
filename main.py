import os
from telegram.ext import ApplicationBuilder, CommandHandler
from commands import (
    start, auth, check, checkall, myxp, mylevel, myprojects,
    myskills, mybadges, logtime, addfriend, removefriend, listfriends
)
from scheduler import start_scheduler

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.environ.get('PORT', 10000))

app = ApplicationBuilder().token(BOT_TOKEN).build()

# Команды
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("auth", auth))
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

# Планировщик
start_scheduler(app)

# Webhook запуск
app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    webhook_url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/"
)
