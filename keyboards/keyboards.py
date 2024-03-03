from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

def main_menu_kb() -> InlineKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    button1 = KeyboardButton(text = "Записать доход")
    button2 = KeyboardButton(text = "Записать расход")
    button3 = KeyboardButton(text = "/help")
    button4 = KeyboardButton(text = "/Баланс")
    button5 = KeyboardButton(text = "/История")

    kb.row(button1, button2, width = 2)
    kb.row(button4, width = 1)
    kb.row(button3, button5, width = 2)

    return kb.as_markup()

def get_inline_keyboard(categories):
    inline_keyboard = InlineKeyboardBuilder()
    for i in categories:
        inline_keyboard.add(InlineKeyboardButton(text = i, callback_data = i))
    inline_keyboard.add(InlineKeyboardButton(text = 'Добавить категории', callback_data = 'add'))
    if len(categories) > 0:
        inline_keyboard.add(InlineKeyboardButton(text = 'Удалить категории', callback_data = 'remove'))
    inline_keyboard.add(InlineKeyboardButton(text = 'Выход', callback_data = 'exit'))
    inline_keyboard.adjust(3)
    return inline_keyboard.as_markup()


def del_category(categories):
    ikb_del = InlineKeyboardBuilder()
    for i in categories:
        ikb_del.add(InlineKeyboardButton(text = i, callback_data = f'del_{i}'))
    ikb_del.add(InlineKeyboardButton(text = 'Выход', callback_data = 'exit'))
    return ikb_del.as_markup()
