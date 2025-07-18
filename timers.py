import asyncio
from database import update_user_time, get_user_time, get_active_users
from aiogram import Bot
from config import ADMIN_ID
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import set_game_state, get_game_state

current_timer = {"user_id": None}
message_data = {"chat_id": None, "message_id": None}
bot: Bot = None
prev_state = {"text": "", "markup": ""}

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
                
                await bot.send_message(
                    message_data["chat_id"],
                    f"⏰ Время {user_name} вышло!"
                )
                current_timer["user_id"] = None

        if message_data["message_id"]:
            await update_timer_message()


async def update_timer_message():
    users = await get_active_users()
    active_id = current_timer["user_id"]

    max_name_length = max((len(u[1]) for u in users), default=0)
    column_width = max(12, max_name_length + 1)

    text_lines = []
    for uid, name, time_sec in users:
        time_str = f"{time_sec // 60:02}:{time_sec % 60:02}"
        padded_name = name.ljust(column_width)
        if uid == active_id:
            line = f"🔥 <b>{padded_name}{time_str}</b>"
        else:
            line = f"🕓 {padded_name}{time_str}"
        text_lines.append(line)
    text = "\n".join(text_lines)

    keyboard = [
        [InlineKeyboardButton(text=u[1], callback_data=f"start_{u[0]}")]
        for u in users
    ]
    keyboard.append([InlineKeyboardButton(text="⏹ Остановить все", callback_data="stop_all")])
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    if text == prev_state["text"] and markup.model_dump_json() == prev_state["markup"]:
        return

    await bot.edit_message_text(
        chat_id=message_data["chat_id"],
        message_id=message_data["message_id"],
        text=f"🕒 Таймеры:\n<pre>{text}</pre>",
        reply_markup=markup,
        parse_mode="HTML"
    )
    prev_state["text"] = text
    prev_state["markup"] = markup.model_dump_json()



async def handle_callback(data: str):
    if data.startswith("start_"):
        uid = int(data.split("_")[1])
        current_timer["user_id"] = uid
    elif data == "stop_all":
        current_timer["user_id"] = None
