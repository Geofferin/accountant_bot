from aiogram import F, types
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

from database.database import Database
from keyboards import keyboards
from keyboards.keyboards import get_inline_keyboard_for_categories, get_simple_inline_kb, main_menu_kb
from states.states import StateFilter, States

"""
TO DO:
    #sentiago
    также стоит сделать такую автоматизацию - чтоб скрипт сам следил за тем, на чьём компе он запускается 
    и в зависимости от этого и подгружал нужный токен - твоего бота или моего
    вполне себе можно так сделать, через переменные среды - туда на обоих компьютерах сохраняем инфу, которая бы определяла наши компы
    а бот при запуске эту инфу чекает и подгружает нужный вариант токена
    
    СДЕЛАТЬ ВСЕ БАЗОВЫЕ ФУНКЦИИ, ЗАБИНДИТЬ ВСЕ КНОПКИ - DONE
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
        убрать глобальные переменные - DONE
        изначально должны вводиться базовые категории, иначе будет None и его нельзя будет убрать
    Остальные:
        запретить добавление дублирующей категории
        Если кто то добавит категорию с названием начинающимся с del_, то вместо записи, категория удалиться
        Проверяет длину категорий целиком, будет ошибка если ввести неget_inline_keyboard_for_categoriesсколько категорий на общую длину 44 символа, а запрет должен касаться только длинны одной категории.
        не дать ввести команду в качестве названия категории
        обработать исключение для ввода слишком большого кол-ва дней, за которые должна выводиться история
    Полировка:
        заменить технические названия и сделать вывод описания в начале, сделать удаление сообщений с командами
        сделать код более читаемым. Разгрузить колбек хендлер и основной файл. Состояния в отдельный файл
"""

router = Router()
BotDB = Database()


@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    if not BotDB.user_exists(message.from_user.id):
        BotDB.add_user(message.from_user.id)
    await state.set_state(States.default)
    await message.bot.send_message(message.from_user.id, "Добро пожаловать!", reply_markup = main_menu_kb())


@router.message(~StateFilter(States.default), Command('cancel'))
async def cancel(message: types.Message, state: FSMContext) -> None:
    await message.answer('Возврат в главное меню')
    await start(message, state)


@router.message(Command("Баланс"))
async def balance(message: types.Message, state: FSMContext) -> None:
    balance = BotDB.get_balance(user_id = message.from_user.id)
    await message.answer(f'Ваш текущий баланс: {round(balance, 2)} ₽')


@router.message(Command("История"))
async def history(message: types.Message, state: FSMContext) -> None:
    await message.bot.send_message(message.from_user.id,
                                   "Вы хотите посмотреть общую историю по всем категориям или историю по отдельным категориям?",
                                   reply_markup = get_simple_inline_kb(1, 'Общая история', 'Отдельные категории'))
    await state.set_state(States.input_choice_for_get_history)


@router.callback_query(StateFilter(States.input_choice_for_get_history), F.data.in_(['Общая история', 'Отдельные категории']))
async def get_history(cb: types.CallbackQuery, state: FSMContext) -> None:
    if cb.data == 'Общая история':
        await state.update_data(history_mode = 'all')
    else:
        categories = BotDB.get_categories(user_id = cb.from_user.id, operation = 'all')
        await cb.message.edit_text(text = 'Отметьте все нужные вам категории в меню ниже',
                                   reply_markup = get_inline_keyboard_for_categories(categories, mode = 'history'))


@router.callback_query(StateFilter(States.input_choice_for_get_history), F.data.startswith('BotCategory_'))
async def set_categories(cb: types.CallbackQuery, state: FSMContext) -> None:
    category = cb.data.split('_')[1]
    kb = cb.message.reply_markup
    for row in kb.inline_keyboard:
        for button in row:
            if button.callback_data.split('_')[1] == category:
                button.text = button.text + ' ✓'
                break
    await cb.message.edit_text(text = cb.message.text, reply_markup = kb)


@router.callback_query(F.data == 'BotMenu_Завершить')
async def get_categories(cb: types.CallbackQuery, state: FSMContext) -> None:
    categories = set()
    for row in cb.message.reply_markup.inline_keyboard:
        for button in row:
            if button.text.endswith(' ✓'):
                category = button.text.strip(' ✓')
                categories.add(category)
    await state.update_data(categories = categories, mode_categories = 'some')
    await cb.message.edit_text("Enter the number of days for which the transaction history is needed")
    await state.set_state(States.input_date)


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
            data = await state.get_data()
            if data['mode_categories'] == 'all':
                history = BotDB.get_history_for_all_categories(period, message.from_user.id)
                await message.answer(history)
            elif data['mode_categories'] == 'some':
                categories = data['categories']
                history =  BotDB.get_history_for_some_categories(message.from_user.id, categories, period)
                await message.answer(history)


@router.message(F.text.in_(["Записать доход", "Записать расход"]))
async def note(message: types.Message, state: FSMContext) -> None:
    if message.text == "Записать доход":
        await state.update_data(operation = 'income')
        operation = True
        categories = BotDB.get_categories(user_id = message.from_user.id, operation = 'income')
    elif message.text == "Записать расход":
        await state.update_data(operation = 'spend')
        operation = False
        categories = BotDB.get_categories(user_id = message.from_user.id, operation = 'spend')
    await message.bot.send_message(message.from_user.id, "Выберите категорию",
                                   reply_markup = keyboards.get_inline_keyboard_for_categories(
                                       categories))


@router.callback_query(F.data.startswith('BotCategory_'), ~StateFilter(States.input_choice_for_get_history))
@router.callback_query(F.data.in_(['add', 'remove', 'exit']))
async def vote_callback(callback: types.CallbackQuery, state: FSMContext):
    action = await state.get_data()
    if callback.data == 'add':
        await callback.bot.send_message(chat_id = callback.message.chat.id,
                                        text = 'Введите название категории\nЕсли их несколько, вводите через пробел')
        await state.set_state(States.input_new_category)

    elif callback.data == 'remove':
        if action['operation'] == 'income':
            categories = BotDB.get_categories(user_id = callback.from_user.id, operation = 'income')
        elif action['operation'] == 'spend':
            categories = BotDB.get_categories(user_id = callback.from_user.id, operation = 'spend')
        await callback.bot.send_message(chat_id = callback.message.chat.id, text = 'Какую категорию удалять?',
                                        reply_markup = keyboards.del_category(categories))

    elif callback.data[
         :4] == 'del_':  # Если кто то добавит категорию с названием начинающимся с del_, то вместо записи, категория удалиться
        BotDB.del_category(user_id = callback.from_user.id, category_del = callback.data.replace('del_', ''),
                           operation = action['operation'])
        await callback.bot.send_message(chat_id = callback.message.chat.id, text = 'Категория удалена')

    elif callback.data == 'exit':
        pass

    else:
        await state.update_data(category = callback.data)
        await callback.bot.send_message(chat_id = callback.message.chat.id, text = 'Введите сумму')
        await state.set_state(States.input_money)
    await callback.message.delete()


@router.message(StateFilter(States.input_new_category))
async def add_category(message: types.Message, state: FSMContext) -> None:
    action = await state.get_data()
    if len(message.text) < 44:  # Проверяет длинну категории целиком, будет ошибка если ввести несколько категорий на общую длинну 44 символа
        for i in message.text.split():  # Специально написал i, потому что в прошлый раз запутался из-за названия переменных
            BotDB.add_category(message.from_user.id, i, operation = action['operation'])
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
            if len(value) < 13:
                action = await state.get_data()
                category = action['category'].split('_')[1]
                if action['operation'] == 'income':
                    BotDB.add_income(message.from_user.id, value, category)
                    await message.answer(f'Доход {value} ₽ записан')
                elif action['operation'] == 'spend':
                    BotDB.add_cost(message.from_user.id, value, category)
                    await message.answer(f'Расход {value} ₽ записан')

            else:
                await message.reply('Неплохо...\nНо я не поверю что ты оперируешь такими суммами)')
        else:
            await message.reply('Сумма должна быть не меньше 0.01 ₽')
