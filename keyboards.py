from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
#button1 = KeyboardButton(text="/help")
button2 = KeyboardButton(text="/earned")
button3 = KeyboardButton(text="/spent")
button4 = KeyboardButton(text="/balance")
button5 = KeyboardButton(text="/history")
main_keyboard.add(button2, button3, button4, button5)


def get_inline_keyboard(categories):
    ikb = InlineKeyboardMarkup(row_width=3) #не работает, всегда 1 клавиша в линии
    for i in categories:
        ikb.add(InlineKeyboardButton(text=i, callback_data=i))
    ikb.add(InlineKeyboardButton(text='Добавить категории', callback_data='add'))
    if len(categories) > 0:
        ikb.add(InlineKeyboardButton(text='Удалить категории', callback_data='del'))
    ikb.add(InlineKeyboardButton(text='Выход', callback_data='exit'))
    return ikb


'''
categories = ['job', 'sale', 'aboba', 'chim-', '-chima']

ikb_e = InlineKeyboardMarkup(row_width=3)
for category in categories:#income_categories:
    ikb_e.add(InlineKeyboardButton(text=category, callback_data=category))
ikb_e.add(InlineKeyboardButton(text='exit', callback_data='exit'))

ikb_s = InlineKeyboardMarkup(row_width=3)
for category in categories:#spend_categories:
    ikb_s.add(InlineKeyboardButton(text=category, callback_data=category))
ikb_s.add(InlineKeyboardButton(text='exit', callback_data='exit'))
'''
