from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
#button1 = KeyboardButton(text="/help")
button2 = KeyboardButton(text="/earned")
button3 = KeyboardButton(text="/spent")
button4 = KeyboardButton(text="/balance")
button5 = KeyboardButton(text="/history")
main_keyboard.add(button2, button3, button4, button5)

# ПОКА НЕ ИСПОЛЬЗУЕТСЯ. ДОБАВИТЬ ВОЗМОЖНОСТЬ ВЫБИРАТЬ ИСТОЧНИК ДОХОДА, ДАЛЕЕ НУЖНО БУДЕТ СДЕЛАТЬ ВОЗМОЖНОСТЬ ДОБАВЛЯТЬ НОВЫЕ ИСТОЧНИКИ И УДАЛЯТЬ ИХ.
ikb_e = InlineKeyboardMarkup(row_width=2)
ib1 = InlineKeyboardButton(text='job', callback_data='job')
ib2 = InlineKeyboardButton(text='sale', callback_data='sale')
ib3 = InlineKeyboardButton(text='exit', callback_data='exit')
ikb_e.add(ib1, ib2, ib3)

# ПОКА НЕ ИСПОЛЬЗУЕТСЯ. ДОБАВИТЬ ВОЗМОЖНОСТЬ ВЫБИРАТЬ СТАТЬЮ РАСХОДА, ДАЛЕЕ НУЖНО БУДЕТ СДЕЛАТЬ ВОЗМОЖНОСТЬ ДОБАВЛЯТЬ НОВЫЕ СТАТЬИ И УДАЛЯТЬ ИХ.
ikb_s = InlineKeyboardMarkup(row_width=2)
ib1 = InlineKeyboardButton(text='rent', callback_data='rent')
ib2 = InlineKeyboardButton(text='food', callback_data='food')
ib3 = InlineKeyboardButton(text='exit', callback_data='exit')
ikb_s.add(ib1, ib2, ib3)
