from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def main_menu_kb() -> InlineKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    button1 = KeyboardButton(text="Записать доход")
    button2 = KeyboardButton(text="Записать расход")
    button3 = KeyboardButton(text="Баланс")
    button4 = KeyboardButton(text="История")
    button5 = KeyboardButton(text="Помощь")

    kb.row(button1, button2, width=2)
    kb.row(button3, button4, width=2)
    kb.row(button5, width=1)

    return kb.as_markup()


def get_inline_keyboard(categories):
    inline_keyboard = InlineKeyboardBuilder()
    for i in categories:
        inline_keyboard.add(InlineKeyboardButton(text=i, callback_data=i))
    inline_keyboard.adjust(3)
    inline_keyboard.row((InlineKeyboardButton(text='Добавить категории', callback_data='add')), width=1)
    if len(categories) > 0:
        inline_keyboard.add(InlineKeyboardButton(text='Удалить категории', callback_data='remove'))
    inline_keyboard.row((InlineKeyboardButton(text='Выход', callback_data='exit')), width=1)
    return inline_keyboard.as_markup()


def del_category(categories):
    ikb_del = InlineKeyboardBuilder()
    for i in categories:
        ikb_del.add(InlineKeyboardButton(text=i, callback_data=f'del_{i}'))
    ikb_del.adjust(3)
    ikb_del.row((InlineKeyboardButton(text='Выход', callback_data='exit')), width=1)
    return ikb_del.as_markup()
