import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from school21_api import authenticate, api_get

# in-memory хранилище
users_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Привет!\n\n"
        "Этот бот был разработан для студентов Школы 21, чтобы отслеживать XP, друзей в кампусе и прогресс по проектам.\n\n"
        "Авторы:\n"
        "Дима — TG: @OdintD | sh21: whirlpon\n"
        "Арси — TG: @arildmt | sh21: fernaani\n"
    )
    keyboard = [
        ["/auth", "/check", "/checkall"],
        ["/myxp", "/mylevel"],
        ["/myprojects", "/myskills", "/mybadges"],
        ["/logtime", "/addfriend", "/removefriend", "/listfriends"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(text, reply_markup=reply_markup)

async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("Использование: /auth <login> <password>")
        return
    login, password = context.args
    at, rt, exp = authenticate(login, password)
    if at is None:
        await update.message.reply_text("Неверный логин или пароль. Попробуйте снова.")
        return
    uid = update.effective_user.id
    users_data[uid] = {
        'login': login,
        'access_token': at,
        'refresh_token': rt,
        'expires_at': exp,
        'friends': []
    }
    await update.message.reply_text(f"Успешно авторизованы как {login}.")

def get_user_data(uid):
    return users_data.get(uid)

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    udata = get_user_data(uid)
    if not udata:
        await update.message.reply_text("Сначала авторизуйтесь через /auth <login> <password>.")
        return
    target = context.args[0] if context.args else udata['login']
    resp, err = api_get(udata, f"/participants/{target}/workstation")
    if err == 'auth_error' or resp is None:
        await update.message.reply_text("Ошибка авторизации, введите /auth заново.")
        return
    if resp.status_code == 200:
        d = resp.json()
        await update.message.reply_text(
            f"{target}: кластер {d['clusterName']}, ряд {d['row']}, место {d['number']}"
        )
    elif resp.status_code == 404:
        await update.message.reply_text(f"{target}: не в кампусе.")
    else:
        await update.message.reply_text("Ошибка получения данных.")

async def addfriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    udata = get_user_data(uid)
    if not udata:
        await update.message.reply_text("Сначала авторизуйтесь через /auth.")
        return
    if not context.args:
        await update.message.reply_text("Использование: /addfriend <login>")
        return
    friend = context.args[0]
    if friend in udata['friends']:
        await update.message.reply_text(f"{friend} уже в списке друзей.")
    else:
        udata['friends'].append(friend)
        await update.message.reply_text(f"Добавлен друг: {friend}")

async def removefriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    udata = get_user_data(uid)
    if not udata:
        await update.message.reply_text("Сначала авторизуйтесь через /auth.")
        return
    if not context.args:
        await update.message.reply_text("Использование: /removefriend <login>")
        return
    friend = context.args[0]
    if friend in udata['friends']:
        udata['friends'].remove(friend)
        await update.message.reply_text(f"Удалён друг: {friend}")
    else:
        await update.message.reply_text(f"{friend} нет в списке друзей.")

async def listfriends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    udata = get_user_data(uid)
    if not udata:
        await update.message.reply_text("Сначала авторизуйтесь через /auth.")
        return
    if not udata['friends']:
        await update.message.reply_text("Список друзей пуст.")
    else:
        await update.message.reply_text("Ваши друзья:\n" + "\n".join(udata['friends']))

async def checkall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    udata = get_user_data(uid)
    if not udata:
        await update.message.reply_text("Сначала авторизуйтесь через /auth.")
        return
    if not udata['friends']:
        await update.message.reply_text("Список друзей пуст. Добавьте через /addfriend.")
        return
    lines = []
    for friend in udata['friends']:
        resp, err = api_get(udata, f"/participants/{friend}/workstation")
        if resp and resp.status_code == 200:
            d = resp.json()
            lines.append(f"{friend}: кластер {d['clusterName']}, ряд {d['row']}, место {d['number']}")
        else:
            lines.append(f"{friend}: не в кампусе.")
    await update.message.reply_text("\n".join(lines))

async def myxp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    udata = get_user_data(uid)
    if not udata:
        await update.message.reply_text("Сначала авторизуйтесь через /auth.")
        return
    resp, _ = api_get(udata, f"/participants/{udata['login']}/experience-history")
    if resp and resp.status_code == 200:
        total = sum(item.get('expValue', 0) for item in resp.json().get('expHistory', []))
        await update.message.reply_text(f"Ваш суммарный XP: {total}")
    else:
        await update.message.reply_text("Ошибка получения XP.")

async def mylevel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    udata = get_user_data(uid)
    if not udata:
        await update.message.reply_text("Сначала авторизуйтесь через /auth.")
        return
    resp, _ = api_get(udata, f"/participants/{udata['login']}")
    if resp and resp.status_code == 200:
        lvl = resp.json().get('level', 'неизвестно')
        await update.message.reply_text(f"Ваш уровень: {lvl}")
    else:
        await update.message.reply_text("Ошибка получения уровня.")

async def myprojects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    udata = get_user_data(uid)
    if not udata:
        await update.message.reply_text("Сначала авторизуйтесь через /auth.")
        return
    resp, _ = api_get(udata, f"/participants/{udata['login']}/projects")
    if resp and resp.status_code == 200:
        projs = resp.json().get('projects', [])
        if not projs:
            await update.message.reply_text("Проекты не найдены.")
        else:
            await update.message.reply_text("Проекты:\n" + "\n".join(p['title'] for p in projs))
    else:
        await update.message.reply_text("Ошибка получения проектов.")

async def myskills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    udata = get_user_data(uid)
    if not udata:
        await update.message.reply_text("Сначала авторизуйтесь через /auth.")
        return
    resp, _ = api_get(udata, f"/participants/{udata['login']}/skills")
    if resp and resp.status_code == 200:
        skills = resp.json().get('skills', [])
        if not skills:
            await update.message.reply_text("Навыки не найдены.")
        else:
            await update.message.reply_text("Навыки:\n" + "\n".join(f"{s['name']}: {s['points']}" for s in skills))
    else:
        await update.message.reply_text("Ошибка получения навыков.")

async def mybadges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    udata = get_user_data(uid)
    if not udata:
        await update.message.reply_text("Сначала авторизуйтесь через /auth.")
        return
    resp, _ = api_get(udata, f"/participants/{udata['login']}/badges")
    if resp and resp.status_code == 200:
        badges = resp.json().get('badges', [])
        if not badges:
            await update.message.reply_text("Значки не найдены.")
        else:
            await update.message.reply_text(
                "Значки:\n" +
                "\n".join(f"{b['name']} ({b['receiptDateTime']})" for b in badges)
            )
    else:
        await update.message.reply_text("Ошибка получения значков.")

async def logtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    udata = get_user_data(uid)
    if not udata:
        await update.message.reply_text("Сначала авторизуйтесь через /auth.")
        return
    resp, _ = api_get(udata, f"/participants/{udata['login']}/logtime")
    if resp and resp.status_code == 200:
        await update.message.reply_text(f"Среднее время в кампусе за неделю: {resp.json()} ч.")
    else:
        await update.message.reply_text("Ошибка получения logtime.")
