import telebot
from telebot import apihelper

import os
from dotenv import load_dotenv
load_dotenv()

import src.cls.commands.start as command_start
import src.cls.commands.init as command_init
import src.cls.commands.puzzle as command_puzzle
import src.cls.commands.me as command_me

from src.ModuleLoader import ModuleLoader
ml = ModuleLoader()

import time
from datetime import datetime, timedelta, timezone

import sqlite3

db_path = './puzzles.db'


# Setup required database tables
(ml.User.User(ml, sqlite3.connect(db_path))).setup_database_structure()
(ml.User.User(ml, sqlite3.connect(db_path))).setup_database_structure_played()


bot = telebot.TeleBot((os.getenv('telegram_token').replace('\\x3a', ':')), parse_mode="Markdown") # type: ignore
apihelper.proxy = {'https': 'socks5://localhost:1080'}

# Handle start command
@bot.message_handler(commands=['start', 'старт'])
def start(message: telebot.types.Message):
    connection = sqlite3.connect(db_path)
    print(datetime.fromtimestamp(time.time(), timezone(timedelta(seconds=abs(time.timezone)))), 'Command execution:', message.from_user.id, 'start') # type: ignore
    command_init.init(ml, connection, bot, message)

    command_start.start(ml, connection, bot, message)


# Handle puzzle command
@bot.message_handler(commands=['puzzle', 'задача'])
def puzzle(message: telebot.types.Message):
    connection = sqlite3.connect(db_path)
    print(datetime.fromtimestamp(time.time(), timezone(timedelta(seconds=abs(time.timezone)))), 'Command execution:', message.from_user.id, 'puzzle') # type: ignore
    command_init.init(ml, connection, bot, message)

    command_puzzle.puzzle(ml, connection, bot, message)


# Handle me command
@bot.message_handler(commands=['me', 'я'])
def me(message: telebot.types.Message):
    connection = sqlite3.connect(db_path)
    print(datetime.fromtimestamp(time.time(), timezone(timedelta(seconds=abs(time.timezone)))), 'Command execution:', message.from_user.id, 'me') # type: ignore
    command_init.init(ml, connection, bot, message)

    command_me.me(ml, connection, bot, message)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message: telebot.types.Message):
    connection = sqlite3.connect(db_path)
    command_init.init(ml, connection, bot, message)

    bot.reply_to(message, 'Неизвестная команда')


# Handle button clicks
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: telebot.types.CallbackQuery):
    print(datetime.fromtimestamp(time.time(), timezone(timedelta(seconds=abs(time.timezone)))), 'Button execution:', call.from_user.id, call.data) # type: ignore
    connection = sqlite3.connect(db_path)
    command_init.init(ml, connection, bot, call) # type: ignore

    if 'Switch to puzzle' in call.data:  # type: ignore
        command_puzzle.select_puzzle_handler(ml, connection, bot, call)

    elif 'Make move' in call.data:  # type: ignore
        command_puzzle.make_move_puzzle_handler(ml, connection, bot, call)

    bot.answer_callback_query(callback_query_id=call.id)

bot.infinity_polling(123)
