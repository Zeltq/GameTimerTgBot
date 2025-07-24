from aiogram import Router, F
from aiogram.types import Message
from config import ADMIN_ID
from database import get_user_by_name, set_user_time, deactivate_user, get_all_users, get_active_users

router = Router()

@router.message(F.text.startswith("/set_time"))
async def set_time(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return await msg.answer("⛔ Только админ.")
    parts = msg.text.split()

    if len(parts) == 2:
        try:
            users = await get_active_users()
            print(f'Введено часов: {parts[1]}')
            print(((float(parts[1])*60)-90-10-10))
            print(users)
            minutes = ((float(parts[1])*60)-90-10-10)/len(users)
            if not users:
                return await msg.answer("Нет пользователей в базе данных.")
            
            for user in users:
                await set_user_time(user[0], minutes*60)
            return await msg.answer("Время установлено")

        except ValueError:
            return await msg.answer("Некорректное количество минут.")
        
    elif len(parts) == 3:
        name, minutes = parts[1], parts[2]
        try:
            minutes = int(minutes)
            user = await get_user_by_name(name)
            if not user:
                return await msg.answer("Пользователь не нейден.")
            await set_user_time(user[0], minutes*60)
            return await msg.answer("Время установлено")
        except ValueError:
            return await msg.answer("Некорректное количество минут.")
    else:
        return await msg.answer("Формат: /set_time [имя] [минуты] или /set_time [часы] ")

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
