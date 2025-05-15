import telebot

import os
from dotenv import load_dotenv
load_dotenv()

import src.cls.commands.start as command_start
import src.cls.commands.init as command_init
import src.cls.commands.puzzle as command_puzzle

from src.ModuleLoader import ModuleLoader
ml = ModuleLoader()

import sqlite3

db_path = './puzzles.db'


# Setup required database tables
(ml.User.User(ml, sqlite3.connect(db_path))).setup_database_structure()


bot = telebot.TeleBot((os.getenv('telegram_token').replace('\\x3a', ':')), parse_mode=None) # type: ignore

# Handle start command
@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    connection = sqlite3.connect(db_path)
    print('Command execution:', message.from_user.id, 'start') # type: ignore
    command_init.init(ml, connection, bot, message)
    command_start.start(ml, connection, bot, message)


# Handle puzzle selection by id
@bot.message_handler(commands=['puzzle'])
def puzzle(message: telebot.types.Message):
    connection = sqlite3.connect(db_path)
    print('Command execution:', message.from_user.id, 'puzzle') # type: ignore
    command_init.init(ml, connection, bot, message)
    command_puzzle.puzzle(ml, connection, bot, message)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message: telebot.types.Message):
    connection = sqlite3.connect(db_path)
    command_init.init(ml, connection, bot, message)
    bot.reply_to(message, 'Unknown action')


bot.infinity_polling()
