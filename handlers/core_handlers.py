from aiogram import F, types
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
import emoji
import asyncio

from database.database import Database
from keyboards import keyboards
from keyboards.keyboards import main_menu_kb
from states.states import StateFilter, States


router = Router()
BotDB = Database()


@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    if not BotDB.user_exists(message.from_user.id):
        BotDB.add_user(message.from_user.id)
    await message.delete()
    await state.set_state(States.default)
    await message.bot.send_message(message.from_user.id, "Добро пожаловать!", reply_markup=main_menu_kb())


@router.message(F.text.in_("Помощь"))
async def help(message: types.Message, state: FSMContext) -> None:
    await message.answer('Что то тут наверное стоило написать...')


@router.message(~StateFilter(States.default), Command('cancel'))
async def cancel(message: types.Message, state: FSMContext) -> None:
    await message.answer('Возврат в главное меню')
    await start(message, state)


@router.message(F.text.in_("Баланс"))
async def balance(message: types.Message, state: FSMContext) -> None:
    balance = BotDB.get_balance(user_id=message.from_user.id)
    await message.answer(f'Ваш текущий баланс: {round(balance, 2)} ₽')
    await message.delete()


@router.message(F.text.in_("История"))
async def history(message: types.Message, state: FSMContext) -> None:
    msg = await message.bot.send_message(message.from_user.id, 'Введите количество дней, за которые необходимо получить историю записей')
    await message.delete()
    await state.set_state(States.input_date)
    asyncio.create_task(delete_message(msg, 10))


@router.message(F.text.in_(["Записать доход", "Записать расход"]))
async def note(message: types.Message, state: FSMContext) -> None:
    if message.text == "Записать доход":
        await state.update_data(operation='income')
        categories = BotDB.get_categories(user_id=message.from_user.id, operation='income')
    elif message.text == "Записать расход":
        await state.update_data(operation='spend')
        categories = BotDB.get_categories(user_id=message.from_user.id, operation='spend')
    await message.delete()
    await message.bot.send_message(message.from_user.id, "Выберите категорию", reply_markup=keyboards.get_inline_keyboard(categories))


@router.callback_query()
async def vote_callback(callback: types.CallbackQuery, state: FSMContext):
    action = await state.get_data()
    if callback.data == 'add':
        msg = await callback.bot.send_message(chat_id=callback.message.chat.id, text='Введите название категории\nЕсли их несколько, вводите через пробел')
        await state.set_state(States.input_new_category)
        asyncio.create_task(delete_message(msg, 10))

    elif callback.data == 'remove':
        if action['operation'] == 'income':
            categories = BotDB.get_categories(user_id=callback.from_user.id, operation='income')
        elif action['operation'] == 'spend':
            categories = BotDB.get_categories(user_id=callback.from_user.id, operation='spend')
        await callback.bot.send_message(chat_id=callback.message.chat.id, text='Какую категорию удалять?', reply_markup=keyboards.del_category(categories))

    elif callback.data[:4] == 'del_':  # Если кто то добавит категорию с названием начинающимся с del_, то вместо записи, категория удалиться
        BotDB.del_category(user_id=callback.from_user.id, category_del=callback.data.replace('del_', ''), operation=action['operation'])
        await callback.bot.send_message(chat_id=callback.message.chat.id, text='Категория удалена')

    elif callback.data == 'exit':
        pass

    else:
        await state.update_data(category=callback.data)
        msg = await callback.bot.send_message(chat_id=callback.message.chat.id, text='Введите сумму')
        await state.set_state(States.input_money)
        asyncio.create_task(delete_message(msg, 10))
    await callback.message.delete()


@router.message(StateFilter(States.input_new_category))
async def add_category(message: types.Message, state: FSMContext) -> None:
    action = await state.get_data()
    for x in message.text.split():
        x = x.replace("'", '').replace('\\', '')
        if action['operation'] == 'income':  # запрашиваем список уже добавленных категорий
            categories = BotDB.get_categories(user_id=message.from_user.id, operation='income')
        elif action['operation'] == 'spend':
            categories = BotDB.get_categories(user_id=message.from_user.id, operation='spend')
        if x not in categories:
            count = 0
            for letter in x:  # каждое отдельное название категории разбиваем на символы, чтобы проверить, не являются ли они эмоджи
                if emoji.is_emoji(letter):
                    count += 3
                else:
                    count += 1
            if count < 44:  # методом тыка, определил, что это максимальная длинна названия, которая не будет ломать бота. Один эмоджи примерно равен 3 обычным символам
                BotDB.add_category(message.from_user.id, x, operation=action['operation'])
                await message.answer(f'Категория: {x} добавлена')
            else:
                await message.reply('Слишком большая длинна категории.\nМаксимальная длинна - 43 символа или 14 эмоджи')
        else:
            await message.answer(f'Категория {x} уже есть в списке')
    await message.delete()


@router.message(StateFilter(States.input_money))
async def load_note(message: types.Message, state: FSMContext) -> None:
    value = message.text.replace(',', '.')
    await message.delete()
    try:
        float(value)
    except ValueError:
        await message.reply('Необходимо ввести число')
    else:
        if float(value) >= 0.01:
            if len(value) < 13:
                action = await state.get_data()
                if action['operation'] == 'income':
                    BotDB.add_income(message.from_user.id, value, action['category'])
                    await message.answer(f'Доход {value} ₽ записан')
                elif action['operation'] == 'spend':
                    BotDB.add_cost(message.from_user.id, value, action['category'])
                    await message.answer(f'Расход {value} ₽ записан')

            else:
                await message.reply('Неплохо...\nНо я не поверю что ты оперируешь такими суммами)')
        else:
            await message.reply('Сумма должна быть не меньше 0.01 ₽')


@router.message(StateFilter(States.input_date))
async def load_history(message: types.Message, state: FSMContext) -> None:
    period = message.text
    await message.delete()
    try:
        int(period)
    except ValueError:
        await message.reply('Нужно ввести число')
    else:
        if int(period) <= 0 or int(period) > 36500:
            await message.reply('Количество дней должно быть больше нуля, но меньше 100 лет')
        else:
            history = BotDB.get_history(period, user_id=message.from_user.id)
            await message.answer(history)


async def delete_message(message: types.Message, sleep_time):
    await asyncio.sleep(sleep_time)
    await message.delete()
