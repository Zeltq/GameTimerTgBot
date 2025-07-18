import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import init_db
from handlers import user, admin, game
from timers import start_timers_loop, set_bot_instance

async def main():
    await init_db()
    bot = Bot(BOT_TOKEN)
    await set_bot_instance(bot)
    dp = Dispatcher()
    dp.include_routers(user.router, admin.router, game.router)
    asyncio.create_task(start_timers_loop())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
