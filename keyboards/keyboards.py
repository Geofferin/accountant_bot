from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
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


def get_inline_keyboard_for_categories(categories, mode: None | str = None):
    inline_keyboard = InlineKeyboardBuilder()
    for category in categories:
        inline_keyboard.add(InlineKeyboardButton(text = category, callback_data = 'BotCategory_' + category))
    if mode is None:
        inline_keyboard.row(InlineKeyboardButton(text = 'Добавить категории', callback_data = 'add'))
        if len(categories) > 0:
            inline_keyboard.add(InlineKeyboardButton(text = 'Удалить категории', callback_data = 'remove'))
    if mode == 'history':
        inline_keyboard.adjust(4)
        inline_keyboard.row(InlineKeyboardButton(text = 'Завершить', callback_data = 'BotMenu_Завершить'))
    inline_keyboard.row(InlineKeyboardButton(text = 'Выход', callback_data = 'BotMenu_exit'))
    return inline_keyboard.as_markup()


def get_simple_inline_kb(width, *args, **kwargs) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(text = button, callback_data = button))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(text = text, callback_data = button))

    kb_builder.row(*buttons, width = width)

    return kb_builder.as_markup()


def del_category(categories):
    ikb_del = InlineKeyboardBuilder()
    for i in categories:
        ikb_del.add(InlineKeyboardButton(text = i, callback_data = f'del_{i}'))
    ikb_del.add(InlineKeyboardButton(text = 'Выход', callback_data = 'exit'))
    return ikb_del.as_markup()
