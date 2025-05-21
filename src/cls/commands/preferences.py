from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader

import sqlite3
import telegram


async def update_rating_difference(ml: 'ModuleLoader', connection: sqlite3.Connection, query: telegram.CallbackQuery):
    p = ml.Preferences.Preferences(ml, connection, searchByUserId=query.from_user.id)
    p.rating_difference = int(query.data.split(':')[1])
    p.update_database_entry()

    await query.message.chat.send_message(f'Целевой рейтинг задан в {('+' if int(query.data.split(':')[1]) > 0 else '') + query.data.split(':')[1]}')


async def preferences(ml: 'ModuleLoader', connection: sqlite3.Connection, message: telegram.Message):
    buttons = [
        [
            telegram.InlineKeyboardButton('-300', callback_data='preferences_rating_difference:-300'),
            telegram.InlineKeyboardButton('-100', callback_data='preferences_rating_difference:-100'),
            telegram.InlineKeyboardButton('0', callback_data='preferences_rating_difference:0'),
            telegram.InlineKeyboardButton('+100', callback_data='preferences_rating_difference:100'),
            telegram.InlineKeyboardButton('+300', callback_data='preferences_rating_difference:300'),
        ]
    ]

    keyboard = telegram.InlineKeyboardMarkup(buttons)

    await message.chat.send_message(f'Здесь можно выбрать:\n1) Целевой рейтинг задач\n\nИзменения вступят в силу начиная со следующей задачи.', reply_markup=keyboard)
