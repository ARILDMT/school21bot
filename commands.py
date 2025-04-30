import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from rocket import send_verification_code, validate_confirmation_code
from school21_api import (
    get_workstation,
    get_xp,
    get_level,
    get_projects,
    get_badges,
    get_skills,
    get_logtime,
)

# ── /start ──────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Привет!\n\n"
        "Этот бот был разработан для студентов Школы 21, чтобы отслеживать XP, "
        "друзей в кампусе и прогресс по проектам.\n\n"
        "Авторы:\n"
        "• Дима — TG: @OdintD | sh21: whirlpon\n"
        "• Арси — TG: @arildmt | sh21: fernaani\n\n"
        "1) Авторизуйтесь: `/auth <login>`\n"
        "2) Введите код: `/confirm <код>`\n\n"
        "После этого остальные команды (`/check`, `/myxp` и т. д.) будут работать автоматически."
    )
    keyboard = [
        ["/auth", "/confirm"],
        ["/check", "/checkall"],
        ["/myxp", "/mylevel"],
        ["/myprojects", "/myskills", "/mybadges"],
        ["/logtime", "/addfriend", "/removefriend", "/listfriends"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(text, reply_markup=reply_markup)


# ── /auth <login> ───────────────────────────────────────────────────────────
async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Использование: /auth <login>")

    login = context.args[0]
    # сохраняем логин
    context.user_data["login"] = login

    try:
        send_verification_code(login)
        await update.message.reply_text(
            "✔ Код подтверждения отправлен вам в Rocket.Chat.\n"
            "Введите `/confirm <код>`."
        )
    except Exception:
        await update.message.reply_text(
            "❌ Не удалось отправить код. Проверьте, пожалуйста, ваш логин."
        )


# ── /confirm <код> ──────────────────────────────────────────────────────────
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "login" not in context.user_data:
        return await update.message.reply_text("Сначала введите `/auth <login>`.")
    if not context.args:
        return await update.message.reply_text("Использование: `/confirm <код>`")

    login = context.user_data["login"]
    code = context.args[0]

    ok, token = validate_confirmation_code(login, code)
    if not ok:
        return await update.message.reply_text("❌ Неверный код, попробуйте ещё раз.")

    # сохраняем админ-токен School21
    context.user_data["school_token"] = token
    await update.message.reply_text("🎉 Вы успешно авторизованы!")


# ── /check [login] ──────────────────────────────────────────────────────────
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = context.args[0] if context.args else None
    if not login:
        return await update.message.reply_text("Использование: /check <login>")
    data = get_workstation(login)
    await update.message.reply_text(
        f"Пользователь `{login}` находится в кластере "
        f"{data['clusterName']} (ряд {data['row']}, место {data['number']})."
    )


# ── /myxp ───────────────────────────────────────────────────────────────────
async def myxp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = context.user_data.get("login")
    if not login:
        return await update.message.reply_text("Сначала `/auth <login>`.")
    data = get_xp(login)
    await update.message.reply_text(f"Ваш суммарный XP: {data['peerReviewPoints'] + data['codeReviewPoints']}")


# ── /mylevel ─────────────────────────────────────────────────────────────────
async def mylevel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = context.user_data.get("login")
    if not login:
        return await update.message.reply_text("Сначала `/auth <login>`.")
    data = get_level(login)
    await update.message.reply_text(f"Ваш уровень: {data['level']} (до следующего: {data['expToNextLevel']} XP)")


# ── /myprojects ─────────────────────────────────────────────────────────────
async def myprojects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = context.user_data.get("login")
    if not login:
        return await update.message.reply_text("Сначала `/auth <login>`.")
    data = get_projects(login)
    lines = [f"{p['title']} — {p['status']}" for p in data["projects"]]
    await update.message.reply_text("Ваши проекты:\n" + "\n".join(lines))


# ── /mybadges ────────────────────────────────────────────────────────────────
async def mybadges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = context.user_data.get("login")
    if not login:
        return await update.message.reply_text("Сначала `/auth <login>`.")
    data = get_badges(login)
    lines = [b["name"] for b in data["badges"]]
    await update.message.reply_text("Ваши значки:\n" + "\n".join(lines))


# ── /myskills ───────────────────────────────────────────────────────────────
async def myskills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = context.user_data.get("login")
    if not login:
        return await update.message.reply_text("Сначала `/auth <login>`.")
    data = get_skills(login)
    lines = [f"{s['name']}: {s['points']}" for s in data["skills"]]
    await update.message.reply_text("Ваши навыки:\n" + "\n".join(lines))


# ── /logtime ────────────────────────────────────────────────────────────────
async def logtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = context.user_data.get("login")
    if not login:
        return await update.message.reply_text("Сначала `/auth <login>`.")
    hours = get_logtime(login)
    await update.message.reply_text(f"Среднее время в кампусе за неделю: {hours:.2f} ч.")


# ── Список друзей ───────────────────────────────────────────────────────────
_friend_list = set()

async def addfriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Использование: /addfriend <login>")
    _friend_list.add(context.args[0])
    await update.message.reply_text("Добавлено в друзья.")

async def removefriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Использование: /removefriend <login>")
    _friend_list.discard(context.args[0])
    await update.message.reply_text("Удалено из друзей.")

async def listfriends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _friend_list:
        return await update.message.reply_text("Список друзей пуст.")
    await update.message.reply_text("Друзья:\n" + "\n".join(_friend_list))

async def checkall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _friend_list:
        return await update.message.reply_text("Список друзей пуст.")
    lines = []
    for peer in _friend_list:
        d = get_workstation(peer)
        lines.append(f"{peer}: {d['clusterName']} {d['row']}{d['number']}")
    await update.message.reply_text("Где друзья:\n" + "\n".join(lines))
