# Telegram bot logic
import telegram
import httpx # Using httpx for async requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler, ContextTypes

# User must replace this with their actual bot token
BOT_TOKEN = "YOUR_BOT_TOKEN" 
# User must replace this with their deployed app URL for webhook
WEBHOOK_URL = "YOUR_WEBHOOK_URL"

# URL of the Flask backend. For local dev, Flask usually runs on port 5000.
# When deployed, this would be the base URL of the Render.org service.
FLASK_BACKEND_URL = "http://localhost:5000" # Adjust if your Flask app runs elsewhere locally

# --- Authentication States for ConversationHandler ---
AUTH_USERNAME, AUTH_PASSWORD = range(2)

# --- Helper function to make API calls to Flask backend ---
async def make_backend_request(method: str, endpoint: str, user_login: str = None, data: dict = None, params: dict = None):
    headers = {}
    if user_login:
        # The backend s21_api_client uses user_login to fetch tokens from DB
        # For /api/pr routes, user_login is also passed as a query param or in JSON body
        # to identify the acting user.
        if params:
            params["user_login"] = user_login
        elif data and method.upper() in ["POST", "PUT"]:
            data["user_login"] = user_login
        # If it's a GET request and no other params, we might need to add user_login as a query param
        elif not params and method.upper() == "GET" and "user_login" not in endpoint:
             params = {"user_login": user_login}

    url = f"{FLASK_BACKEND_URL}{endpoint}"
    
    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            if method.upper() == "GET":
                response = await client.get(url, params=params, headers=headers)
            elif method.upper() == "POST":
                response = await client.post(url, json=data, params=params, headers=headers)
            # Add other methods like PUT, DELETE if needed
            else:
                return {"error": "Unsupported HTTP method"}, 500
            
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            return response.json(), response.status_code
        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                return error_data, e.response.status_code
            except json.JSONDecodeError:
                return {"error": "HTTP error", "details": str(e.response.text)}, e.response.status_code
        except httpx.RequestError as e:
            return {"error": "Request to backend failed", "details": str(e)}, 503

# --- Bot Command Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "Привет! Я бот S21 PeerConnect. Я помогу тебе с организацией peer-to-peer ревью "
        "и предоставлю информацию из твоего профиля Школы 21.\n\n"
        "Для начала работы, пожалуйста, авторизуйся. Используй команду /auth."
    )
    # Clear any previous auth state
    context.user_data.pop("authenticated_user_login", None)
    context.user_data.pop("s21_access_token", None) # Bot doesn't store this long-term, backend does
    await update.message.reply_text(welcome_message)
    return ConversationHandler.END # End any previous conversation

async def auth_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("authenticated_user_login"):
        await update.message.reply_text(f"Вы уже авторизованы как {context.user_data['authenticated_user_login']}. Для смены пользователя используйте /start, затем /auth.")
        return ConversationHandler.END
    await update.message.reply_text("Пожалуйста, введите ваш логин от Школы 21:")
    return AUTH_USERNAME

async def auth_receive_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["auth_attempt_username"] = update.message.text
    await update.message.reply_text("Теперь введите ваш пароль от Школы 21:")
    return AUTH_PASSWORD

async def auth_receive_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = context.user_data.get("auth_attempt_username")
    password = update.message.text
    telegram_id = update.effective_user.id

    await update.message.reply_text("Проверяю ваши данные... Пожалуйста, подождите.")

    response_data, status_code = await make_backend_request(
        method="POST",
        endpoint="/api/auth/login",
        data={"username": username, "password": password, "telegram_id": telegram_id}
    )

    if status_code == 200 and response_data.get("user_school21_login"):
        context.user_data["authenticated_user_login"] = response_data["user_school21_login"]
        # Bot doesn't need to store the access_token itself, backend manages it with refresh_token
        await update.message.reply_text(f"Авторизация успешна! Вы вошли как {response_data['user_school21_login']}. Теперь доступны все команды.")
    else:
        error_msg = response_data.get("error", "Неизвестная ошибка авторизации.")
        details_msg = response_data.get("details", "")
        await update.message.reply_text(f"Ошибка авторизации: {error_msg} {details_msg}. Попробуйте /auth еще раз.")
        context.user_data.pop("authenticated_user_login", None)
    
    context.user_data.pop("auth_attempt_username", None)
    return ConversationHandler.END

async def auth_cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("auth_attempt_username", None)
    context.user_data.pop("authenticated_user_login", None)
    await update.message.reply_text("Авторизация отменена. Вы можете начать заново с /auth.")
    return ConversationHandler.END

async def ensure_auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_login = context.user_data.get("authenticated_user_login")
    if not user_login:
        await update.message.reply_text("Пожалуйста, сначала авторизуйтесь с помощью команды /auth.")
        return None
    return user_login

# --- S21 Data Commands (using the new backend structure) ---
async def s21_data_command_template(update: Update, context: ContextTypes.DEFAULT_TYPE, s21_endpoint: str, display_name: str):
    user_login = await ensure_auth(update, context)
    if not user_login: return

    await update.message.reply_text(f"Запрашиваю {display_name} для {user_login}...")
    response_data, status_code = await make_backend_request(
        method="GET", 
        endpoint=f"/s21_api/{s21_endpoint}", 
        user_login=user_login # This will be added as ?user_login=... by make_backend_request
    )

    if status_code == 200:
        # Prettify JSON for display or extract key info
        if isinstance(response_data, dict) or isinstance(response_data, list):
            reply_text = f"**{display_name}:**\n```json\n{json.dumps(response_data, indent=2, ensure_ascii=False)}\n```"
            if s21_endpoint == "me":
                reply_text = f"**Профиль ({user_login}):**\nЛогин: {response_data.get('login', 'N/A')}\nEmail: {response_data.get('email', 'N/A')}\nИмя: {response_data.get('firstName', '')} {response_data.get('lastName', '')}\nУровень: {response_data.get('level', 'N/A')}"
            elif s21_endpoint == "mypoints":
                reply_text = f"**XP ({user_login}):** {response_data.get('totalXp', 'N/A')}"
            # Add more custom formatting for other endpoints if needed
        else:
            reply_text = str(response_data) # Fallback for non-dict/list data
        await update.message.reply_text(reply_text, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)
    else:
        error_msg = response_data.get("error", "Ошибка")
        details_msg = response_data.get("details", "Не удалось получить данные.")
        await update.message.reply_text(f"Ошибка при запросе {display_name}: {error_msg} ({details_msg})")

async def myprofile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await s21_data_command_template(update, context, "me", "Мой профиль")

async def myxp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await s21_data_command_template(update, context, "mypoints", "Мой XP")

async def mylevel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 'mylevel' is part of 'me' endpoint in the current backend implementation
    user_login = await ensure_auth(update, context)
    if not user_login: return
    await update.message.reply_text(f"Запрашиваю уровень для {user_login}...")
    response_data, status_code = await make_backend_request("GET", f"/s21_api/me", user_login=user_login)
    if status_code == 200 and isinstance(response_data, dict):
        await update.message.reply_text(f"**Ваш уровень ({user_login}):** {response_data.get('level', 'N/A')}")
    else:
        await update.message.reply_text("Не удалось получить данные об уровне.")

async def myprojects_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await s21_data_command_template(update, context, "myprojects", "Мои проекты")

# Placeholder for other S21 commands from screenshot - map to backend if available
async def myskills_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Assuming /s21_api/myskills exists or will be added to backend
    await s21_data_command_template(update, context, "myskills", "Мои навыки") 

async def mybadges_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await s21_data_command_template(update, context, "mybadges", "Мои значки")

async def logtime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await s21_data_command_template(update, context, "logtime", "Мой логтайм")

# --- Peer Review Calendar Commands ---
async def view_slots_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_login = await ensure_auth(update, context)
    if not user_login: return

    month_filter = None
    if context.args and len(context.args) > 0:
        month_filter = context.args[0] # Expects YYYY-MM
        # Basic validation for YYYY-MM format can be added here

    params = {"user_login": user_login}
    if month_filter:
        params["month"] = month_filter
    
    await update.message.reply_text(f"Запрашиваю слоты peer review (Месяц: {month_filter or 'все'})...")
    response_data, status_code = await make_backend_request("GET", "/api/pr/slots", params=params)

    if status_code == 200 and isinstance(response_data, list):
        if not response_data:
            await update.message.reply_text("Свободных или забронированных слотов не найдено.")
            return
        message = "**Доступные и забронированные слоты:**\n"
        for slot in response_data:
            start = datetime.fromisoformat(slot['start_time']).strftime('%d.%m %H:%M')
            end = datetime.fromisoformat(slot['end_time']).strftime('%H:%M')
            project = slot.get('project_name', 'N/A')
            status = slot.get('status', 'N/A')
            creator = slot.get('creator_user_login', 'N/A')
            booker = slot.get('booker_user_login', 'N/A')
            message += f"ID: {slot['id']}, Создатель: {creator}, Проект: {project}, {start} - {end}, Статус: {status}" 
            if status == 'booked': message += f", Забронировал: {booker}"
            message += "\n"
        await update.message.reply_text(message, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)
    else:
        await update.message.reply_text("Не удалось загрузить слоты.")

async def create_slot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_login = await ensure_auth(update, context)
    if not user_login: return

    if len(context.args) < 2:
        await update.message.reply_text("Использование: /create_slot YYYY-MM-DDTHH:MM YYYY-MM-DDTHH:MM [название_проекта]")
        return
    
    start_time_str = context.args[0]
    end_time_str = context.args[1]
    project_name = " ".join(context.args[2:]) if len(context.args) > 2 else None

    payload = {
        "start_time": start_time_str,
        "end_time": end_time_str,
        "project_name": project_name,
        "user_login": user_login # Backend expects user_login for creator
    }
    await update.message.reply_text("Создаю слот...")
    response_data, status_code = await make_backend_request("POST", "/api/pr/slots", data=payload)

    if status_code == 201:
        slot = response_data
        await update.message.reply_text(f"Слот создан успешно! ID: {slot['id']}")
    else:
        error = response_data.get("error", "Неизвестная ошибка")
        await update.message.reply_text(f"Ошибка создания слота: {error}")

async def book_slot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_login = await ensure_auth(update, context)
    if not user_login: return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Использование: /book_slot <ID_слота>")
        return
    slot_id = int(context.args[0])

    await update.message.reply_text(f"Бронирую слот ID {slot_id} для вас ({user_login})...")
    # user_login is passed in the payload for the backend to identify the booker
    response_data, status_code = await make_backend_request("POST", f"/api/pr/slots/{slot_id}/book", data={"user_login": user_login})

    if status_code == 200:
        await update.message.reply_text("Слот успешно забронирован!")
    else:
        error = response_data.get("error", "Неизвестная ошибка")
        await update.message.reply_text(f"Ошибка бронирования слота: {error}")

async def cancel_slot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_login = await ensure_auth(update, context)
    if not user_login: return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Использование: /cancel_slot <ID_слота>")
        return
    slot_id = int(context.args[0])

    await update.message.reply_text(f"Отменяю слот ID {slot_id} (если вы создатель или бронировали его)... ")
    response_data, status_code = await make_backend_request("POST", f"/api/pr/slots/{slot_id}/cancel", data={"user_login": user_login})

    if status_code == 200:
        await update.message.reply_text("Слот успешно отменен/статус обновлен.")
    else:
        error = response_data.get("error", "Неизвестная ошибка")
        await update.message.reply_text(f"Ошибка отмены слота: {error}")

# --- Other Commands (Placeholders for now, map to backend if needed) ---
async def confirm_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_login = await ensure_auth(update, context)
    if not user_login: return
    await update.message.reply_text("Команда /confirm. (Функционал будет доработан)")

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_login = await ensure_auth(update, context)
    if not user_login: return
    await update.message.reply_text("Команда /check. (Функционал будет доработан)")

async def checkall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_login = await ensure_auth(update, context)
    if not user_login: return
    await update.message.reply_text("Команда /checkall. (Функционал будет доработан)")

async def addfriend_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_login = await ensure_auth(update, context)
    if not user_login: return
    await update.message.reply_text("Команда /addfriend. (Функционал будет доработан)")

async def removefriend_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_login = await ensure_auth(update, context)
    if not user_login: return
    await update.message.reply_text("Команда /removefriend. (Функционал будет доработан)")

async def listfriends_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_login = await ensure_auth(update, context)
    if not user_login: return
    await update.message.reply_text("Команда /listfriends. (Функционал будет доработан)")

# --- Generic Handlers ---
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Извините, я не понимаю эту команду. Используйте /start для начала.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Update {update} caused error {context.error}")
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("Произошла ошибка при обработке вашего запроса. Попробуйте позже.")

def setup_telegram_bot(flask_app_instance):
    # ConversationHandler for /auth command
    auth_handler = ConversationHandler(
        entry_points=[CommandHandler("auth", auth_start_command)],
        states={
            AUTH_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth_receive_username)],
            AUTH_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth_receive_password)],
        },
        fallbacks=[CommandHandler("cancel_auth", auth_cancel_command), CommandHandler("start", start_command)],
        per_user=True, # Store conversation state per user
        per_chat=True  # And per chat
    )

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(auth_handler) # Add the conversation handler for auth
    
    # S21 Data Commands
    application.add_handler(CommandHandler("myprofile", myprofile_command)) # Using 'me' endpoint
    application.add_handler(CommandHandler("myxp", myxp_command))
    application.add_handler(CommandHandler("mylevel", mylevel_command))
    application.add_handler(CommandHandler("myprojects", myprojects_command))
    application.add_handler(CommandHandler("myskills", myskills_command))
    application.add_handler(CommandHandler("mybadges", mybadges_command))
    application.add_handler(CommandHandler("logtime", logtime_command))

    # Peer Review Calendar Commands
    application.add_handler(CommandHandler("view_slots", view_slots_command))
    application.add_handler(CommandHandler("create_slot", create_slot_command))
    application.add_handler(CommandHandler("book_slot", book_slot_command))
    application.add_handler(CommandHandler("cancel_slot", cancel_slot_command))

    # Other commands from screenshot (currently placeholders)
    application.add_handler(CommandHandler("confirm", confirm_command))
    application.add_handler(CommandHandler("check", check_command))
    application.add_handler(CommandHandler("checkall", checkall_command))
    application.add_handler(CommandHandler("addfriend", addfriend_command))
    application.add_handler(CommandHandler("removefriend", removefriend_command))
    application.add_handler(CommandHandler("listfriends", listfriends_command))

    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    application.add_error_handler(error_handler)

    flask_app_instance.extensions["telegram_bot_app"] = application
    flask_app_instance.extensions["telegram_bot_token"] = BOT_TOKEN 

    print("Telegram bot application configured with command handlers.")
    # ... (rest of the print statements for guidance)

