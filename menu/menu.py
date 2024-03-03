from aiogram import Bot
from aiogram.types import BotCommand


async def set_menu(bot: Bot):
    menu = [
        BotCommand(command = '/start', description = 'Начать работу с бухгалтерским ботом'),
        BotCommand(command = '/cancel', description = "отменить текущую операцию"),
        BotCommand(command = '/help', description = 'in progress...')
    ]
    await bot.set_my_commands(menu)
