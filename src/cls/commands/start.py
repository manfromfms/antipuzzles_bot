from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader

import sqlite3
import telebot

def start(ml: 'ModuleLoader', connection: sqlite3.Connection, bot: telebot.TeleBot, message: telebot.types.Message):
    bot.reply_to(message, 'Бот с задачами по antichess.\n' \
                    '[GitHub](https://github.com/manfromfms/antipuzzles_bot)\n\n' \
                    'Список команд:\n\n' \
                    '/puzzle\n' \
                    '\tБез аргументов - текущая задача\n' \
                    '\tid:[число] - информация о задаче\n\n' \
                    'Пример использования команд: /puzzle id:1238'
                )