from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from config import ADMIN_ID
from database import get_active_users, set_message_id, reset_message_ids
from timers import update_timer_message, handle_callback
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()

@router.message(F.text == "/start_game")
async def start_game(msg: Message, bot: Bot):
    if msg.from_user.id != ADMIN_ID:
        return await msg.answer("⛔ Только админ.")
    users = await get_active_users()
    if not users:
        return await msg.answer("Нет активных игроков.")
    
    logger.info("Starting game, resetting message IDs")
    await reset_message_ids()
    
    for user in users:
        user_id, _, _, chat_id, message_id = user
        if message_id:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception as e:
                logger.error(f"Ошибка удаления старого сообщения для {chat_id}: {e}")
        
        try:
            message = await bot.send_message(chat_id, "Запуск таймеров...")
            await set_message_id(user_id, message.message_id)
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения пользователю {user_id}: {e}")
    
    logger.info("Forcing timer message update")
    await update_timer_message(force=True)

@router.callback_query()
async def process_button(callback: CallbackQuery):
    await handle_callback(callback.data)
    await callback.answer()