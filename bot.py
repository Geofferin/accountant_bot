from aiogram import executor
from dispatcher import dp
import handlers

from db import BotDB
BotDB = BotDB('accountant.db')


async def startup(_):
    print('bot successfully launched')


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=startup, skip_updates=True)
