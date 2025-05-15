from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader

import sqlite3
import telebot

def start(ml: 'ModuleLoader', connection: sqlite3.Connection, bot: telebot.TeleBot, message: telebot.types.Message):
    bot.reply_to(message, 'Hello!')