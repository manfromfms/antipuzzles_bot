from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader

import sqlite3
import telebot

# This function is supposed to make a new entry of a user in the database. The function must be silent.
def init(ml: 'ModuleLoader', connection: sqlite3.Connection, bot: telebot.TeleBot, message: telebot.types.Message):
    bot.reply_to(message, 'INIT')