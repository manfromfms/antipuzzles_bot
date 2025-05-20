from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

import logging
from typing import Optional

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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.WARN
)
logging.getLogger("httpx").setLevel(logging.WARNING)


# Setup required database tables
(ml.User.User(ml, sqlite3.connect(db_path))).setup_database_structure()
(ml.User.User(ml, sqlite3.connect(db_path))).setup_database_structure_played()
(ml.Preferences.Preferences(ml, sqlite3.connect(db_path))).setup_database_structure()

app = ApplicationBuilder().token((os.getenv('telegram_token').replace('\\x3a', ':'))).build() # type: ignore

# Handle start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    connection = sqlite3.connect(db_path)
    message = update.message

    logging.info('Command execution:', message.from_user.id, 'start') # type: ignore
    
    await command_init.init(ml, connection, message) # type: ignore
    await command_start.start(ml, connection, message) # type: ignore
app.add_handler(CommandHandler(['start'], start))


# Handle puzzle command
async def puzzle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    connection = sqlite3.connect(db_path)
    message = update.message

    logging.info('Command execution:', message.from_user.id, 'puzzle') # type: ignore

    await command_init.init(ml, connection, message) # type: ignore
    await command_puzzle.puzzle(ml, connection, message) # type: ignore
app.add_handler(CommandHandler(['puzzle'], puzzle))

# Handle me command
async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    connection = sqlite3.connect(db_path)
    message = update.message

    logging.info('Command execution:', message.from_user.id, 'me') # type: ignore
    
    await command_init.init(ml, connection, message) # type: ignore
    await command_me.me(ml, connection, message) # type: ignore
app.add_handler(CommandHandler(['me'], me))

'''
# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message: telebot.types.Message):
    connection = sqlite3.connect(db_path)
    command_init.init(ml, connection, bot, message)

    bot.reply_to(message, 'Неизвестная команда')
'''

# Handle button clicks
async def callback_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    connection = sqlite3.connect(db_path)

    query = update.callback_query
    message = query.message
    logging.info('Button execution:', query.from_user.id, query.data) # type: ignore
    
    await command_init.init(ml, connection, message) # type: ignore

    if 'Switch to puzzle' in query.data:  # type: ignore
        await command_puzzle.select_puzzle_handler(ml, connection, query) # type: ignore

    elif 'Make move' in query.data:  # type: ignore
        await command_puzzle.make_move_puzzle_handler(ml, connection, query) # type: ignore

    await query.answer() # type: ignore
app.add_handler(CallbackQueryHandler(callback_inline))

app.run_polling()
