from aiogram import types
from dispatcher import dp
import config
import re
from bot import BotDB
from keyboards import main_keyboard, ikb_e, ikb_s
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData


"""
TO DO:
    СДЕЛАТЬ ВСЕ БАЗОВЫЕ ФУНКЦИИ, ЗАБИНДИТЬ ВСЕ КНОПКИ - DONE
    РАЗОБРАТЬСЯ В ОСТАЛЬНЫХ ФАЙЛАХ В ПРОЕКТЕ - ALMOST
    ДОБАВИТЬ ИСТОЧНИКИ ДОХОДА И СТАТЬИ РАСХОДА:
        список должен открываться после кнопки earned или spent, последний пункт в списке должен позволять добавление нового источника или статьи
        1. добавить столбцы для категорий в обе таблицы - DONE
        2. ВРЕМЕННО. сделать запись тестовой категории, иначе бот не будет работать. - DONE
        3. добавить клавиатуру со стандартными категориями, переписать логику так, чтобы сначала открывалась она и после выбора категории можно было ввести сумму - DONE
        4. прописать возможность добавлять свои категории
        5. при выводе истории должны запрашиваться конкретные категории, записи по которым и будут выводиться. Но также оставить возможность выводить всю историю.
    ДОБАВИТЬ НЕОБЯЗАТЕЛЬНОЕ ОПИСАНИЕ ЗАПИСИ. П-ЛЬ МОЖЕТ ДАТЬ ОПИСАНИЕ, А МОЖЕТ НЕ ДАВАТЬ.
"""


class States(StatesGroup):

    input_money = State()
    input_date = State()


operation = True  # Отделяет расход от дохода. True = доход, False = расход.
category = ''  # Категория дохода или расхода


@dp.message_handler(commands="start")
async def start(message: types.Message):
    if (not BotDB.user_exists(message.from_user.id)):
        BotDB.add_user(message.from_user.id)

    await message.bot.send_message(message.from_user.id, "Welcome!", reply_markup=main_keyboard)


@dp.message_handler(commands=("earned", "spent"))
async def note(message: types.Message, state: FSMContext) -> None:
    global operation
    if message.text == "/earned":
        operation = True
        await message.bot.send_message(message.from_user.id, "Select an income category", reply_markup=ikb_e)
    elif message.text == "/spent":
        operation = False
        await message.bot.send_message(message.from_user.id, "Select a spending category", reply_markup=ikb_s)


@dp.callback_query_handler()
async def vote_callback(callback: types.CallbackQuery):
    if callback.data != 'exit':
        global category
        category = callback.data
        await callback.bot.send_message(chat_id=callback.message.chat.id, text='Enter the amount')
        await States.input_money.set()
    await callback.message.delete()


@dp.message_handler(state=States.input_money)
async def load_note(message: types.Message, state: FSMContext) -> None:
    value = message.text.replace(',', '.')
    try:
        float(value)
    except ValueError:
        await message.reply('You must enter a number')
    else:
        if float(value) >= 0.01:
            if len(value) < 13:  # Можно было добавить через and выше, но пришлось бы писать об этом в ошибке, мало кто будет вводить гигантские числа
                if operation:
                    BotDB.add_income(message.from_user.id, value, category)
                    await message.answer(f'Nice, you earned {value} money\nIncome is recorded')
                    await state.finish()
                if not operation:
                    BotDB.add_cost(message.from_user.id, value, category)
                    await message.answer(f'Spending {value} money is recorded')
                    await state.finish()
            else:
                await message.reply('Неплохо...\nНо я не поверю что ты оперируешь такими суммами)')
        else:
            await message.reply('Сумма должна быть не меньше 0.01 ₽')


@dp.message_handler(commands="balance")
async def balance(message: types.Message, state: FSMContext) -> None:
    balance = BotDB.get_balance(user_id=message.from_user.id)
    await message.answer(f'Current balance is: {round(balance, 2)} ₽')


@dp.message_handler(commands="history")
async def history(message: types.Message, state: FSMContext) -> None:
    await message.bot.send_message(message.from_user.id, "Enter the number of days for which the transaction history is needed")
    await States.input_date.set()


@dp.message_handler(state=States.input_date)  # Не помешала бы сортировка по дате и времени для всего списка, а не для доходов и расходов по отдельности.
async def load_history(message: types.Message, state: FSMContext) -> None:
    period = message.text
    try:
        int(period)
    except ValueError:
        await message.reply('You must enter a number')
    else:
        if int(period) <= 0:
            await message.reply('The number of days must be greater than zero')
        else:
            history = BotDB.get_history(period, user_id=message.from_user.id)
            await message.answer(history)
            await state.finish()

# СТАРЫЕ МЕТОДЫ
# @dp.message_handler(commands=("s", "e"), commands_prefix="/!")
# async def start(message: types.Message):
#     cmd_variants = (('/spent', '/s'), ('/earned', '/e'))
#     operation = '-' if message.text.startswith(cmd_variants[0]) else '+'
#
#     # удаляем команду из сообщения, оставляем только саму сумму
#     value = message.text
#     for command in cmd_variants:
#         for j in command:
#             value = value.replace(j, '').strip()
#
#     # убираем все лишние символы из суммы, оставляя только цифры
#     if(len(value)):
#         x = re.findall(r"\d+(?:.\d+)?", value)
#         if(len(x)):
#             value = float(x[0].replace(',', '.'))
#
#             BotDB.add_record(message.from_user.id, operation, value)
#
#             if operation == '-':
#                 await message.reply("✅ Запись о <u><b>расходе</b></u> успешно внесена!")
#             else:
#                 await message.reply("✅ Запись о <u><b>доходе</b></u> успешно внесена!")
#         else:
#             await message.reply("Не удалось определить сумму!")
#     else:
#         await message.reply("Не введена сумма!")

# @dp.message_handler(commands = ("history", "h"), commands_prefix = "/!")
# async def start(message: types.Message):
#     cmd_variants = ('/history', '/h', '!history', '!h')
#     within_als = {
#         "day": ('today', 'day', 'сегодня', 'день'),
#         "month": ('month', 'месяц'),
#         "year": ('year', 'год'),
#     }
#
#     cmd = message.text
#     for r in cmd_variants:
#         cmd = cmd.replace(r, '').strip()
#
#     within = 'day'
#     if(len(cmd)):
#         for k in within_als:
#             for als in within_als[k]:
#                 if(als == cmd):
#                     within = k
#     print(within)
#
#     records = BotDB.get_records(message.from_user.id, within)
#
#     if len(records):
#         answer = f"🕘 История операций за {within_als[within][-1]}\n\n"
#
#         for r in records:
#             answer += "<b>" + ("➖ Расход" if not r[2] else "➕ Доход") + "</b>"
#             answer += f" - {r[3]}"
#             answer += f" <i>({r[4]})</i>\n"
#
#         await message.reply(answer)
#     else:
#         await message.reply("Записей не обнаружено!")
