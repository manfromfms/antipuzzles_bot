from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader

import sqlite3
import telebot
from telebot.types import ReplyKeyboardRemove

def start(ml: 'ModuleLoader', connection: sqlite3.Connection, bot: telebot.TeleBot, message: telebot.types.Message):
    bot.reply_to(message, 'Бот с задачами по antichess.\n' \
                    '[GitHub](https://github.com/manfromfms/antipuzzles_bot)\n\n' \
                    'Список команд:\n\n' \
                    '/puzzle\n' \
                    '\tБез аргументов - текущая позиция\n' \
                    '\tid:[число] - информация о задаче\n\n' \
                    'Пример использования команд:\n`/puzzle id:1238\n\n`' \
                    'Иногда из-за нестабильности подключения бот может не отпрвить новую позицию, но засчитать ход. Один вариант решения этой проблемы - попросить текущую позицию через /puzzle.'
                ,reply_markup=ReplyKeyboardRemove())