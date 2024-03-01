from aiogram import F, types

from database.database import Database
from aiogram.filters.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.filters import CommandStart, Command

from keyboards import keyboards
from keyboards.keyboards import main_keyboard
from states.states import States, StateFilter

"""
TO DO:
    СДЕЛАТЬ ВСЕ БАЗОВЫЕ ФУНКЦИИ, ЗАБИНДИТЬ ВСЕ КНОПКИ - DONE
    РАЗОБРАТЬСЯ В ОСТАЛЬНЫХ ФАЙЛАХ В ПРОЕКТЕ - ALMOST
    ДОБАВИТЬ ИСТОЧНИКИ ДОХОДА И СТАТЬИ РАСХОДА:
        список должен открываться после кнопки earned или spent, последний пункт в списке должен позволять добавление нового источника или статьи
        1. добавить столбцы для категорий в обе таблицы - DONE
        2. ВРЕМЕННО. сделать запись тестовой категории, иначе бот не будет работать. - DONE
        3. добавить клавиатуру со стандартными категориями, переписать логику так, чтобы сначала открывалась она и после выбора категории можно было ввести сумму - DONE
        4. прописать возможность добавлять свои категории - DONE
        5. при выводе истории должны запрашиваться конкретные категории, записи по которым и будут выводиться. Но также оставить возможность выводить всю историю.
    ДОБАВИТЬ НЕОБЯЗАТЕЛЬНОЕ ОПИСАНИЕ ЗАПИСИ. П-ЛЬ МОЖЕТ ДАТЬ ОПИСАНИЕ, А МОЖЕТ НЕ ДАВАТЬ.
    
Баги:
    Критические:
        бот сыпется, если слишком большая длина одной категории. сделать обработку
        глобальные переменные
        изначально должны вводиться базовые категории, иначе будет None и его нельзя будет убрать
    Остальные:
        запретить добавление дублирующей категории
        Если кто то добавит категорию с названием начинающимся с del_, то вместо записи, категория удалиться
        Проверяет длинну категории целиком, будет ошибка если ввести несколько категорий на общую длинну 44 символа
        не дать ввести команду в качестве названия категории
    Полировка:
        заменить технические названия и сделать вывод описания в начале, сделать удаление сообщений с командами
        сделать код более читаемым. Разгрузить колбек хендлер и основной файл. Состояния в отдельный файл
"""

router = Router()
BotDB = Database()

#От этой хуйни надо избавляться
operation = True  # Отделяет расход от дохода. True = доход, False = расход.
category = ''  # Категория дохода или расхода


@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    if (not BotDB.user_exists(message.from_user.id)):
        BotDB.add_user(message.from_user.id)
    await state.set_state(States.default)
    await message.bot.send_message(message.from_user.id, "Добро пожаловать!", reply_markup=main_keyboard)


@router.message(Command("Баланс"))
async def balance(message: types.Message, state: FSMContext) -> None:
    balance = BotDB.get_balance(user_id=message.from_user.id)
    await message.answer(f'Ваш текущий баланс: {round(balance, 2)} ₽')

# сейчас кнопки выглядят хуево, с / в начале. а хендлер для записи вообще улавливает все сообщения. Ни один хендлер для работы с сообщениями, разместить ниже не получится
# можно попробовать запихнуть все в один

@router.message(Command("История"))
async def history(message: types.Message, state: FSMContext) -> None:
    await message.bot.send_message(message.from_user.id,
                                   "Enter the number of days for which the transaction history is needed")
    await state.set_state(States.input_date)


@router.message(F.text.in_(["Записать доход", "Записать расход"]))
async def note(message: types.Message, state: FSMContext) -> None:
    global operation
    print(message.text)
    if message.text == "Записать доход":
        operation = True
        categories = BotDB.get_categories(user_id=message.from_user.id, operation='income')
    elif message.text == "Записать расход":
        operation = False
        categories = BotDB.get_categories(user_id=message.from_user.id, operation='spend')
    await message.bot.send_message(message.from_user.id, "Выберите категорию",
                                   reply_markup= keyboards.get_inline_keyboard(categories))


@router.callback_query()
async def vote_callback(callback: types.CallbackQuery, state: FSMContext):
    print(callback.data)
    if callback.data == 'add':
        await callback.bot.send_message(chat_id=callback.message.chat.id, text='Введите название категории\nЕсли их несколько, вводите через пробел')
        await state.set_state(States.input_new_category)

    elif callback.data == 'remove':  # Эту фигню надо вынести в отдельную функцию
        if operation:
            categories = BotDB.get_categories(user_id=callback.from_user.id, operation='income')
        if not operation:
            categories = BotDB.get_categories(user_id=callback.from_user.id, operation='spend')
        await callback.bot.send_message(chat_id=callback.message.chat.id, text='Какую категорию удалять?', reply_markup= keyboards.del_category(categories))

    elif callback.data[:4] == 'del_': # Если кто то добавит категорию с названием начинающимся с del_, то вместо записи, категория удалиться
        BotDB.del_category(user_id=callback.from_user.id, category_del=callback.data.replace('del_', ''), operation=operation)
        await callback.bot.send_message(chat_id=callback.message.chat.id, text='Категория удалена')

    elif callback.data == 'exit':
        pass

    else:
        global category
        category = callback.data
        await callback.bot.send_message(chat_id=callback.message.chat.id, text='Введите сумму')
        await state.set_state(States.input_money)
    await callback.message.delete()


@router.message(StateFilter(States.input_new_category))
async def add_category(message: types.Message, state: FSMContext) -> None:
    if len(message.text) < 44:  # Проверяет длинну категории целиком, будет ошибка если ввести несколько категорий на общую длинну 44 символа
        BotDB.add_category(message.from_user.id, f' {message.text}', operation)
        await message.answer(f'Категории добавлены')
    else:
        await message.reply('Максимальная длинна названия - 43 символа')


@router.message(StateFilter(States.input_money))
async def load_note(message: types.Message, state: FSMContext) -> None:
    value = message.text.replace(',', '.')
    try:
        float(value)
    except ValueError:
        await message.reply('Необходимо ввести число')
    else:
        if float(value) >= 0.01:
            if len(value) < 13:  # Можно было добавить через and выше, но пришлось бы писать об этом в ошибке, мало кто будет вводить гигантские числа
                if operation:
                    BotDB.add_income(message.from_user.id, value, category)
                    await message.answer(f'Доход {value} ₽ записан')
         
                if not operation:
                    BotDB.add_cost(message.from_user.id, value, category)
                    await message.answer(f'Расход {value} ₽ записан')
         
            else:
                await message.reply('Неплохо...\nНо я не поверю что ты оперируешь такими суммами)')
        else:
            await message.reply('Сумма должна быть не меньше 0.01 ₽')


@router.message(StateFilter(States.input_date))
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
 
