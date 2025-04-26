from telegram import Update
from telegram.ext import ContextTypes

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет!\n\n"
        "Этот бот был разработан для студентов Школы 21, чтобы отслеживать XP, друзей в кампусе и прогресс по проектам.\n\n"
        "Авторы: Дима:TG @OdintD sh21: whirlpon ; Арси TG @arildmt sh21: fernaani \n"
        "Есть идеи или хотите дополнить бота? Пишите прямо в личку!"
    )

# Команда /setlogin
async def setlogin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Команда /setlogin ещё не реализована.")

# Команда /check
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Команда /check ещё не реализована.")

# Команда /myxp
async def myxp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Команда /myxp ещё не реализована.")

# Команда /mylevel
async def mylevel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Команда /mylevel ещё не реализована.")

# Команда /myprojects
async def myprojects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Команда /myprojects ещё не реализована.")

# Команда /mybadges
async def mybadges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Команда /mybadges ещё не реализована.")

# Команда /myskills
async def myskills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Команда /myskills ещё не реализована.")

# Команда /logtime
async def logtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Команда /logtime ещё не реализована.")

# Команда /addfriend
async def addfriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Команда /addfriend ещё не реализована.")

# Команда /removefriend
async def removefriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Команда /removefriend ещё не реализована.")

# Команда /listfriends
async def listfriends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Команда /listfriends ещё не реализована.")

# Команда /checkall
async def checkall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Команда /checkall ещё не реализована.")
