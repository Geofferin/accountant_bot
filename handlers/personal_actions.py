from aiogram import types

import keyboards
from dispatcher import dp
import config
import re
from bot import BotDB
from keyboards import main_keyboard, get_inline_keyboard
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton



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
    input_new_category = State()

#От этой хуйни надо избавляться
operation = True  # Отделяет расход от дохода. True = доход, False = расход.
category = ''  # Категория дохода или расхода


@dp.message_handler(commands="start")
async def start(message: types.Message):
    if (not BotDB.user_exists(message.from_user.id)):
        BotDB.add_user(message.from_user.id)

    await message.bot.send_message(message.from_user.id, "Welcome!", reply_markup=main_keyboard)


@dp.message_handler(commands=("earned", "spent"))
async def note(message: types.Message, state: FSMContext) -> None:
    #ikb = InlineKeyboardMarkup(row_width=3) #не работает, всегда 1 клавиша в линии
    global operation
    if message.text == "/earned":
        operation = True
        categories = BotDB.get_categories(user_id=message.from_user.id, operation='income')
    elif message.text == "/spent":
        operation = False
        categories = BotDB.get_categories(user_id=message.from_user.id, operation='spend')
    await message.bot.send_message(message.from_user.id, "Выберите категорию", reply_markup=keyboards.get_inline_keyboard(categories))


@dp.callback_query_handler()
async def vote_callback(callback: types.CallbackQuery):
    if callback.data == 'add':
        await callback.bot.send_message(chat_id=callback.message.chat.id, text='Введите название категории\nЕсли их несколько, вводите через пробел')
        await States.input_new_category.set()
    if callback.data == 'del':
        #del_category()
        pass #РАБОТАЕМ
    if callback.data not in ['exit', 'add', 'del']:
        global category
        category = callback.data
        await callback.bot.send_message(chat_id=callback.message.chat.id, text='Введите сумму')
        await States.input_money.set()
    await callback.message.delete()


@dp.message_handler(state=States.input_new_category)
async def add_category(message: types.Message, state: FSMContext) -> None:
    new_category = message.text
    BotDB.add_category(message.from_user.id, new_category, operation)
    await message.answer(f'Категории добавлены')
    await state.finish()


def del_category(message: types.Message, state: FSMContext) -> None:
    categories = BotDB.get_categories(user_id=message.from_user.id, operation='spend')
    get_inline_keyboard(categories)

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
