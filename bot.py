import asyncio
import logging

from aiogram import Bot, Dispatcher
from config.config import *
from handlers import core_handlers
from states.states import storage
# from menu.menu import set_menu
from database.database import Database

db = Database()

async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher(storage=storage)
    # dp.startup.register(set_menu)
    dp.include_router(core_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
