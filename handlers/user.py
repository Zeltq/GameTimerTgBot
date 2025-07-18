from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from state import Registration
from database import add_user
from database import format_active_players

router = Router()

@router.message(F.text == "/start")
async def cmd_start(msg: Message, state: FSMContext):
    await msg.answer("Введите ваше имя:")
    await state.set_state(Registration.waiting_for_name)

@router.message(Registration.waiting_for_name)
async def set_name(msg: Message, state: FSMContext):
    name = msg.text.strip()
    await add_user(msg.from_user.id, name)
    await msg.answer(f"Привет, {name}! Ты в пуле игроков.")
    await state.clear()

@router.message(F.text == "/players")
async def show_players(msg: Message):
    text = await format_active_players()
    await msg.answer(f"👥 Участники:\n{text}")
