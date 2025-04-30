import datetime
from rocket import send_verification_code, validate_confirmation_code 
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from db import (
    set_user_login, get_user_login, 
    add_friend, remove_friend, get_friends,
    add_peer_review, get_peer_reviews, remove_peer_review
)
from rocket import send_verification_code, validate_confirmation_code
from school21_api import (
    fetch_user_workstation, fetch_user_xp, fetch_user_level,
    fetch_user_projects, fetch_user_skills, fetch_user_badges,
    fetch_user_logtime
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 *Добро пожаловать!*\n\n"
        "Этот бот помогает студентам Школы 21:\n"
        "- Отслеживать, кто в кампусе\n"
        "- Собирать друзей и напоминания\n"
        "- Планировать peer-review\n\n"
        "Команды:\n"
        "/auth `<login>` — получить код в Rocket.Chat\n"
        "/confirm `<код>` — ввести код и активировать бота\n"
        "/check `[login]` — проверить кампус\n"
        "/checkall — сразу всех друзей\n"
        "/addfriend `<login>` /removefriend `<login>`\n"
        "/listfriends — список друзей\n"
        "/setreview `<login>` `<YYYY-MM-DDTHH:MM>`\n"
        "/listreviews /removereview `<id>`\n"
        "/myxp /mylevel /myprojects /myskills /mybadges /logtime"
    )
    kb = [
        ["/check","/checkall"],["/myxp","/mylevel"],
        ["/myprojects","/myskills"],["/addfriend","/removefriend"],
        ["/setreview","/listreviews"]
    ]
    await update.message.reply_text(
        text, 
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )

async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    if not context.args:
        return await update.message.reply_text("Используйте: /auth <login>")
    login = context.args[0]
    set_user_login(tg_id, login)
    ok = send_verification_code(login, tg_id)
    msg = "Код отправлен в Rocket.Chat!" if ok else "Ошибка при отправке кода."
    await update.message.reply_text(msg)

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    if not context.args:
        return await update.message.reply_text("Используйте: /confirm <код>")
    code = context.args[0]
    if validate_confirmation_code(tg_id, code):
        await update.message.reply_text("✅ Вы успешно авторизованы!")
    else:
        await update.message.reply_text("❌ Неверный код. Попробуйте ещё раз.")

# ——— Проверки кампуса —————————————————————————————
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    login = context.args[0] if context.args else get_user_login(tg_id)
    if not login:
        return await update.message.reply_text("Сначала /auth <login>!")
    data = fetch_user_workstation(login)
    if data and data.get("clusterId"):
        text = f"✅ `{login}` сейчас в {data['clusterName']} (ряд {data['row']}, место {data['number']})"
    else:
        text = f"❌ `{login}` сейчас не в кампусе"
    await update.message.reply_text(text, parse_mode="Markdown")

async def checkall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    friends = get_friends(tg_id)
    if not friends:
        return await update.message.reply_text("У вас нет друзей. /addfriend")
    msgs = []
    for fr in friends:
        data = fetch_user_workstation(fr)
        status = "в кампусе" if data and data.get("clusterId") else "не в кампусе"
        msgs.append(f"- `{fr}`: {status}")
    await update.message.reply_text("\n".join(msgs), parse_mode="Markdown")

# ——— Друзья —————————————————————————————————————————
async def addfriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    if not context.args:
        return await update.message.reply_text("Используйте: /addfriend <login>")
    add_friend(tg_id, context.args[0])
    await update.message.reply_text("✅ Друг добавлен!")

async def removefriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    if not context.args:
        return await update.message.reply_text("Используйте: /removefriend <login>")
    remove_friend(tg_id, context.args[0])
    await update.message.reply_text("✅ Друг удалён!")

async def listfriends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    lst = get_friends(tg_id)
    text = "Список друзей:\n" + "\n".join(f"- {l}" for l in lst) if lst else "У вас нет друзей."
    await update.message.reply_text(text)

# ——— Peer-review в календаре ——————————————————————————
async def setreview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    if len(context.args) < 2:
        return await update.message.reply_text("Используйте: /setreview <login> <YYYY-MM-DDTHH:MM>")
    login, date = context.args[0], context.args[1]
    # проверка формата ISO
    try:
        datetime.datetime.fromisoformat(date)
    except ValueError:
        return await update.message.reply_text("Неверный формат даты.")
    add_peer_review(tg_id, login, date)
    await update.message.reply_text("✅ Peer-review запланирован.")

async def listreviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    evs = get_peer_reviews(tg_id)
    if not evs:
        return await update.message.reply_text("Нет запланированных peer-review.")
    text = "\n".join(f"{e['id']}: {e['login']} @ {e['date']}" for e in evs)
    await update.message.reply_text(text)

async def removereview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Используйте: /removereview <id>")
    remove_peer_review(int(context.args[0]))
    await update.message.reply_text("✅ Удалено.")

# ——— Личные данные —————————————————————————————————————
async def myxp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    login = get_user_login(tg_id)
    data = fetch_user_xp(login)
    await update.message.reply_text(f"PeerReview: {data['peerReviewPoints']}\n"
                                    f"CodeReview: {data['codeReviewPoints']}\n"
                                    f"Coins: {data['coins']}")

async def mylevel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    login = get_user_login(tg_id)
    lvl = fetch_user_level(login)
    await update.message.reply_text(f"Уровень: {lvl['level']}\nXP: {lvl['exp']}")

async def myprojects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    login = get_user_login(tg_id)
    projs = fetch_user_projects(login)["projects"]
    msg = "\n".join(f"{p['title']} — {p['status']}" for p in projs)
    await update.message.reply_text(msg or "Нет проектов.")

async def myskills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    login = get_user_login(tg_id)
    skills = fetch_user_skills(login)["skills"]
    msg = "\n".join(f"{s['name']}: {s['points']}" for s in skills)
    await update.message.reply_text(msg or "Нет навыков.")

async def mybadges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    login = get_user_login(tg_id)
    badges = fetch_user_badges(login)["badges"]
    msg = "\n".join(b["name"] for b in badges)
    await update.message.reply_text(msg or "Нет значков.")

async def logtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    login = get_user_login(tg_id)
    t = fetch_user_logtime(login)
    await update.message.reply_text(f"Среднее время: {t} часов")
