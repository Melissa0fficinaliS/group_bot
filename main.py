import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from handlers.access import router as access_router
from handlers.adminka import router as admin_router
from handlers.members import router as members_router
from handlers.start import router as start_router


def register_routers(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(access_router)
    dp.include_router(admin_router)
    dp.include_router(members_router)


logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    register_routers(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
