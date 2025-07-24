import re
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database import add_user
from database import format_active_players, delete_user_by_id

class Registration(StatesGroup):
    waiting_for_name = State()

router = Router()

@router.message(F.text == "/start")
async def cmd_start(msg: Message, state: FSMContext):
    await delete_user_by_id(msg.from_user.id)
    await msg.answer("Введите ваше имя (одно слово, до 11 символов):")
    await state.set_state(Registration.waiting_for_name)

@router.message(Registration.waiting_for_name)
async def set_name(msg: Message, state: FSMContext):
    name = msg.text.strip()
    if ' ' in name or len(name) > 11 or not re.match(r'^[a-zA-Zа-яА-Я]+$', name):
        await msg.answer("Имя должно быть одним словом и короче 11 символов, пошел нахуй, попробуй еще раз!")
        return
    if await add_user(msg.from_user.id, name, msg.chat.id):
        await msg.answer(f"Привет, {name}! Ты в пуле игроков.")
        await state.clear()
    else:
        await msg.answer("Это имя уже занято, пошел нахуй, выбери другое!")


@router.message(F.text == "/players")
async def show_players(msg: Message):
    text = await format_active_players()
    await msg.answer(f"👥 Участники:\n{text}")
