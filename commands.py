import os
from telegram import Update
from telegram.ext import ContextTypes
import school21_api as api

# Временное хранилище: Telegram user ID → login школы
user_logins = {}

def get_login(update: Update):
    tg_id = update.effective_user.id
    return user_logins.get(tg_id)

# /setlogin <school_login>
async def setlogin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Пример: /setlogin workerom")
        return
    tg_id = update.effective_user.id
    user_logins[tg_id] = context.args[0]
    await update.message.reply_text(f"Логин {context.args[0]} сохранён.")

# /check <login>
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Пример: /check bibikov-lukyan")
        return
    login = context.args[0]
    result = api.check_user_online(login)
    await update.message.reply_text(result)

# /myxp
async def myxp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = get_login(update)
    if not login:
        await update.message.reply_text("Сначала введи логин через /setlogin <логин>")
        return
    result = api.get_user_xp(login)
    await update.message.reply_text(result)

# /mylevel
async def mylevel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = get_login(update)
    if not login:
        await update.message.reply_text("Сначала введи логин через /setlogin <логин>")
        return
    result = api.get_user_level(login)
    await update.message.reply_text(result)

# /myprojects
async def myprojects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = get_login(update)
    if not login:
        await update.message.reply_text("Сначала введи логин через /setlogin <логин>")
        return
    result = api.get_user_projects(login)
    await update.message.reply_text(result)

# /mybadges
async def mybadges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = get_login(update)
    if not login:
        await update.message.reply_text("Сначала введи логин через /setlogin <логин>")
        return
    result = api.get_user_badges(login)
    await update.message.reply_text(result)

# /myskills
async def myskills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = get_login(update)
    if not login:
        await update.message.reply_text("Сначала введи логин через /setlogin <логин>")
        return
    result = api.get_user_skills(login)
    await update.message.reply_text(result)

# /logtime
async def logtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = get_login(update)
    if not login:
        await update.message.reply_text("Сначала введи логин через /setlogin <логин>")
        return
    result = api.get_user_logtime(login)
    await update.message.reply_text(result)

# Временное хранилище друзей
friends = set()

# /addfriend <login>
async def addfriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Пример: /addfriend fernaani")
        return
    login = context.args[0]
    friends.add(login)
    await update.message.reply_text(f"{login} добавлен в список друзей.")

# /removefriend <login>
async def removefriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Пример: /removefriend fernaani")
        return
    login = context.args[0]
    friends.discard(login)
    await update.message.reply_text(f"{login} удалён из списка друзей.")

# /listfriends
async def listfriends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not friends:
        await update.message.reply_text("У тебя пока нет друзей в списке.")
    else:
        await update.message.reply_text("Твои друзья:\n" + "\n".join(friends))

# /checkall
async def checkall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not friends:
        await update.message.reply_text("Список друзей пуст.")
        return
    messages = []
    for login in friends:
        status = api.check_user_online(login)
        messages.append(f"{login}: {status}")
    await update.message.reply_text("\n\n".join(messages))
