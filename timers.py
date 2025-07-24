import asyncio
import logging
from database import update_user_time, get_user_time, get_active_users, set_game_state, get_game_state
from aiogram import Bot
from config import ADMIN_ID
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

current_timer = {"user_id": None}
bot: Bot = None
prev_states = {}

async def set_bot_instance(b):
    global bot
    bot = b

async def start_timers_loop():
    while True:
        await asyncio.sleep(1)
        user_id = current_timer["user_id"]
        if user_id:
            await update_user_time(user_id, 1)
            time_left = await get_user_time(user_id)
            if time_left <= 0:
                users = await get_active_users()
                user_name = next((u[1] for u in users if u[0] == user_id), str(user_id))
                for _, _, _, chat_id, _ in users:
                    try:
                        await bot.send_message(chat_id, f"⏰ Время {user_name} вышло!")
                    except Exception as e:
                        logger.error(f"Ошибка отправки уведомления в {chat_id}: {e}")
                current_timer["user_id"] = None
                await set_game_state("current_timer", None)
        
        await update_timer_message()

async def update_timer_message(force=False):
    logger.debug(f"Updating timer messages for all users, force={force}")
    users = await get_active_users()
    active_id = current_timer["user_id"]

    max_name_length = max((len(u[1]) for u in users), default=0)
    column_width = max(12, max_name_length + 1)

    text_lines = []
    for uid, name, time_sec, _, _ in users:
        time_str = "00:00" if time_sec <= 0 else f"{time_sec // 60:02}:{time_sec % 60:02}"
        padded_name = name.ljust(column_width)
        if uid == active_id:
            line = f"🔥 <b>{padded_name}{time_str}</b>"
        else:
            line = f"🕓 {padded_name}{time_str}"
        text_lines.append(line)
    text = "\n".join(text_lines)

    keyboard = [
        [InlineKeyboardButton(text=u[1], callback_data=f"start_{u[0]}")]
        for u in users if u[2] > 0
    ]
    keyboard.append([InlineKeyboardButton(text="⏹ Остановить все", callback_data="stop_all")])
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    for _, _, _, chat_id, message_id in users:
        if not message_id:
            continue
        current_state = {"text": text, "markup": markup.model_dump_json()}
        prev_state = prev_states.get(chat_id, {"text": "", "markup": ""})


        if not force and text == prev_state["text"] and markup.model_dump_json() == prev_state["markup"]:
            continue

        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"🕒 Таймеры:\n<pre>{text}</pre>",
                reply_markup=markup,
                parse_mode="HTML"
            )
            prev_states[chat_id] = current_state
        except Exception as e:
            logger.error(f"Ошибка обновления сообщения для {chat_id}: {e}")

async def handle_callback(data: str):
    logger.info(f"Processing callback: {data}")
    if data.startswith("start_"):
        uid = int(data.split("_")[1])
        time_left = await get_user_time(uid)
        if time_left <= 0:
            logger.warning(f"Attempt to start timer for user {uid} with time_left <= 0")
            return
        current_timer["user_id"] = uid
        await set_game_state("current_timer", str(uid))
    elif data == "stop_all":
        current_timer["user_id"] = None
        await set_game_state("current_timer", None)