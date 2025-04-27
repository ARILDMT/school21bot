import os
from telegram.ext import ApplicationBuilder, CommandHandler
import commands

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.environ.get('PORT', 8080))

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", commands.start))
    app.add_handler(CommandHandler("auth", commands.auth))
    app.add_handler(CommandHandler("check", commands.check))
    app.add_handler(CommandHandler("checkall", commands.checkall))
    app.add_handler(CommandHandler("addfriend", commands.addfriend))
    app.add_handler(CommandHandler("removefriend", commands.removefriend))
    app.add_handler(CommandHandler("listfriends", commands.listfriends))
    app.add_handler(CommandHandler("myxp", commands.myxp))
    app.add_handler(CommandHandler("mylevel", commands.mylevel))
    app.add_handler(CommandHandler("myprojects", commands.myprojects))
    app.add_handler(CommandHandler("myskills", commands.myskills))
    app.add_handler(CommandHandler("mybadges", commands.mybadges))
    app.add_handler(CommandHandler("logtime", commands.logtime))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/"
    )
