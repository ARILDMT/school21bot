import os
import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from rocket import send_verification_code, validate_confirmation_code
from school21_api import (
    authenticate,
    get_workstation,
    get_points,
    get_participant,
    get_projects,
    get_skills,
    get_badges,
    get_logtime
)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        DATA = json.load(f)
else:
    DATA = {}

def _save():
    with open(DATA_FILE, "w") as f:
        json.dump(DATA, f, indent=2)

def _get_user(chat_id: int) -> dict:
    return DATA.setdefault(str(chat_id), {
        "login": None,
        "tokens": None,
        "friends": []
    })

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Привет!\n\n"
        "1️⃣ /auth <login> <password> — авторизация\n"
        "2️⃣ /check [login] — где человек\n"
        "3️⃣ /checkall — где ваши друзья\n"
        "4️⃣ /addfriend <login> 5️⃣ /removefriend <login>\n"
        "6️⃣ /listfriends — список друзей\n"
        "7️⃣ /myxp, /mylevel, /myprojects, /myskills, /mybadges, /logtime\n"
    )
    kb = [
        ["/auth","/check","/checkall"],
        ["/addfriend","/removefriend","/listfriends"],
        ["/myxp","/mylevel","/myprojects"],
        ["/myskills","/mybadges","/logtime"],
    ]
    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if len(context.args) != 2:
        return await update.message.reply_text("Использование: /auth <login> <password>")
    login, pwd = context.args
    try:
        tokens = authenticate(login, pwd)
    except Exception as e:
        return await update.message.reply_text(f"Ошибка авторизации: {e}")
    user = _get_user(chat_id)
    user["login"] = login
    user["tokens"] = tokens
    _save()
    await update.message.reply_text("✅ Успешно авторизованы!")

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = _get_user(chat_id)
    if not user["login"]:
        return await update.message.reply_text("Сначала /auth")
    if len(context.args) != 1:
        return await update.message.reply_text("Использование: /confirm <код>")
    code = context.args[0]
    ok = validate_confirmation_code(user["login"], code)
    await update.message.reply_text("✅ Код подтверждён!" if ok else "❌ Неверный код.")

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = _get_user(chat_id)
    if not user["login"]:
        return await update.message.reply_text("Сначала /auth")
    target = context.args[0] if context.args else user["login"]
    try:
        ws = get_workstation(target, user)
        await update.message.reply_text(
            f"{target} в {ws['clusterName']} ⌚ ряд {ws['row']} место {ws['number']}"
        )
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

async def checkall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = _get_user(chat_id)
    lines = []
    for f in user["friends"]:
        try:
            ws = get_workstation(f, user)
            lines.append(f"{f}: {ws['clusterName']} {ws['row']}{ws['number']}")
        except:
            lines.append(f"{f}: ошибка")
    await update.message.reply_text("\n".join(lines) or "У вас нет друзей")

async def addfriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not context.args:
        return await update.message.reply_text("Использование: /addfriend <login>")
    u = _get_user(chat_id)
    lr = context.args[0]
    if lr not in u["friends"]:
        u["friends"].append(lr)
        _save()
        await update.message.reply_text(f"✅ {lr} добавлен в друзья")
    else:
        await update.message.reply_text("Уже в списке")

async def removefriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not context.args:
        return await update.message.reply_text("Использование: /removefriend <login>")
    u = _get_user(chat_id)
    lr = context.args[0]
    if lr in u["friends"]:
        u["friends"].remove(lr)
        _save()
        await update.message.reply_text(f"✅ {lr} удалён из друзей")
    else:
        await update.message.reply_text("Такого нет")

async def listfriends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    u = _get_user(chat_id)
    await update.message.reply_text("\n".join(u["friends"]) or "Список пуст")

async def myxp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    u = _get_user(chat_id)
    if not u["login"]:
        return await update.message.reply_text("Сначала /auth")
    try:
        pts = get_points(u["login"], u)
        await update.message.reply_text(
            f"PeerReview: {pts['peerReviewPoints']}\n"
            f"CodeReview: {pts['codeReviewPoints']}\n"
            f"Coins: {pts['coins']}"
        )
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

async def mylevel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    u = _get_user(chat_id)
    if not u["login"]:
        return await update.message.reply_text("Сначала /auth")
    try:
        p = get_participant(u["login"], u)
        await update.message.reply_text(
            f"Уровень: {p['level']}\n"
            f"XP: {p['expValue']} / {p['expToNextLevel']}"
        )
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

async def myprojects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    u = _get_user(chat_id)
    if not u["login"]:
        return await update.message.reply_text("Сначала /auth")
    try:
        lst = get_projects(u["login"], u)["projects"]
        lines = [f"{p['title']} — {p['status']}" for p in lst]
        await update.message.reply_text("\n".join(lines) or "Нет проектов")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

async def myskills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    u = _get_user(chat_id)
    if not u["login"]:
        return await update.message.reply_text("Сначала /auth")
    try:
        lst = get_skills(u["login"], u)["skills"]
        lines = [f"{s['name']}: {s['points']}" for s in lst]
        await update.message.reply_text("\n".join(lines) or "Нет навыков")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

async def mybadges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    u = _get_user(chat_id)
    if not u["login"]:
        return await update.message.reply_text("Сначала /auth")
    try:
        lst = get_badges(u["login"], u)["badges"]
        lines = [b["name"] for b in lst]
        await update.message.reply_text("\n".join(lines) or "Нет значков")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

async def logtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    u = _get_user(chat_id)
    if not u["login"]:
        return await update.message.reply_text("Сначала /auth")
    try:
        lt = get_logtime(u["login"], u)
        await update.message.reply_text(
            f"Среднее время за неделю: {lt.get('logtimeWeeklyAvgHours')} ч."
        )
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")
