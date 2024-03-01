from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
button2 = KeyboardButton(text="Записать доход")
button3 = KeyboardButton(text="Записать расход")
button4 = KeyboardButton(text="/Баланс")
button5 = KeyboardButton(text="/История")

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                    keyboard = [[
    button2, button3, button4, button5
]])
#button1 = KeyboardButton(text="/help")



def get_inline_keyboard(categories):
    # ikb = InlineKeyboardMarkup(row_width=3)#не работает, всегда 1 клавиша в линии
    inline_keyboard = InlineKeyboardBuilder()
    for i in categories:
        inline_keyboard.add(InlineKeyboardButton(text=i, callback_data=i))
    inline_keyboard.add(InlineKeyboardButton(text='Добавить категории', callback_data='add'))
    if len(categories) > 0:
        inline_keyboard.add(InlineKeyboardButton(text='Удалить категории', callback_data='remove'))
    inline_keyboard.add(InlineKeyboardButton(text='Выход', callback_data='exit'))
    inline_keyboard.adjust(3)
    return inline_keyboard.as_markup()


def del_category(categories):
    ikb_del = InlineKeyboardMarkup(row_width=3)  # не работает, всегда 1 клавиша в линии
    for i in categories:
        ikb_del.add(InlineKeyboardButton(text=i, callback_data=f'del_{i}'))
    ikb_del.add(InlineKeyboardButton(text='Выход', callback_data='exit'))
    return ikb_del
