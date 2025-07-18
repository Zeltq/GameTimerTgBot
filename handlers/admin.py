from aiogram import Router, F
from aiogram.types import Message
from config import ADMIN_ID
from database import get_user_by_name, set_user_time, deactivate_user

router = Router()

@router.message(F.text.startswith("/set_time"))
async def set_time(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return await msg.answer("⛔ Только админ.")
    parts = msg.text.split()
    if len(parts) != 3:
        return await msg.answer("Формат: /set_time [имя] [минуты]")
    name, minutes = parts[1], int(parts[2])
    user = await get_user_by_name(name)
    if not user:
        return await msg.answer("Пользователь не найден.")
    await set_user_time(user[0], minutes * 60)
    await msg.answer(f"✅ Время для {name} установлено: {minutes} мин.")

@router.message(F.text.startswith("/remove"))
async def remove_user(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return await msg.answer("⛔ Только админ.")
    parts = msg.text.split()
    if len(parts) != 2:
        return await msg.answer("Формат: /remove [имя]")
    name = parts[1]
    user = await get_user_by_name(name)
    if not user:
        return await msg.answer("Пользователь не найден.")
    await deactivate_user(user[0])
    await msg.answer(f"🚫 {name} удалён из раунда.")
