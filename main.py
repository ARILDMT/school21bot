import os
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import BotCommand
from commands import (
    setlogin, check, myxp, mylevel, myprojects, mybadges,
    myskills, logtime, addfriend, removefriend,
    listfriends, checkall, start
)

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.environ.get('PORT', 8080))  # Render использует переменную PORT

commands = [
    BotCommand("start", "Запустить бота и узнать информацию"),
    BotCommand("setlogin", "Установить логин для входа"),
    BotCommand("check", "Проверить себя в кампусе"),
    BotCommand("myxp", "Показать свой опыт (XP)"),
    BotCommand("mylevel", "Показать свой уровень"),
    BotCommand("myprojects", "Показать свои проекты"),
    BotCommand("mybadges", "Показать свои бейджи"),
    BotCommand("myskills", "Показать свои навыки"),
    BotCommand("logtime", "Отметить своё время"),
    BotCommand("addfriend", "Добавить друга для отслеживания"),
    BotCommand("removefriend", "Удалить друга из списка"),
    BotCommand("listfriends", "Показать список друзей"),
    BotCommand("checkall", "Проверить всех друзей в кампусе")
]

async def setup_commands(app):
    await app.bot.set_my_commands(commands)

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Установить команды меню
    asyncio.run(setup_commands(app))

    # Обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setlogin", setlogin))
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

    # Запустить бота через Webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/"
    )
