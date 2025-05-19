from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader

import sqlite3
import telebot
from telebot.types import ReplyKeyboardRemove

def me(ml: 'ModuleLoader', connection: sqlite3.Connection, bot: telebot.TeleBot, message: telebot.types.Message):
    user = ml.User.User(ml, connection, searchById=message.from_user.id) # type: ignore
    bot.reply_to(message, f'Рейтинг: {int(user.elo)}±{int(user.elodev)}')