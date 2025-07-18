from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from config import ADMIN_ID
from database import get_active_users
from timers import message_data, update_timer_message, handle_callback

router = Router()

@router.message(F.text == "/start_game")
async def start_game(msg: Message, bot: Bot):
    if msg.from_user.id != ADMIN_ID:
        return await msg.answer("⛔ Только админ.")
    users = await get_active_users()
    if not users:
        return await msg.answer("Нет активных игроков.")
    message = await msg.answer("Запуск таймеров...")
    message_data["chat_id"] = msg.chat.id
    message_data["message_id"] = message.message_id
    await update_timer_message()

@router.callback_query()
async def process_button(callback: CallbackQuery):
    await handle_callback(callback.data)
    await callback.answer()
