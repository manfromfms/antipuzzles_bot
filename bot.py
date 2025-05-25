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
import src.cls.commands.preferences as command_preferences
import src.cls.commands.top as command_top
import src.cls.commands.hardest as command_hardest

from src.ModuleLoader import ModuleLoader
ml = ModuleLoader()

import time
from datetime import datetime, timedelta, timezone

import sqlite3

db_path = './puzzles.db'

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger()


# Setup required database tables
(ml.User.User(ml, sqlite3.connect(db_path))).setup_database_structure()
(ml.User.User(ml, sqlite3.connect(db_path))).setup_database_structure_played()
(ml.Preferences.Preferences(ml, sqlite3.connect(db_path))).setup_database_structure()
(ml.PuzzleVote.PuzzleVote(ml, sqlite3.connect(db_path))).setup_database_structure()

app = ApplicationBuilder()\
    .token((os.getenv('telegram_token')\
    .replace('\\x3a', ':')))\
    .read_timeout(7)\
    .get_updates_read_timeout(42)\
    .build()


# Handle start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    connection = sqlite3.connect(db_path)
    message = update.message

    logger.info(('Command execution:', message.from_user.id, 'start')) # type: ignore
    
    await command_init.init(ml, connection, message) # type: ignore
    await command_start.start(ml, connection, message) # type: ignore
app.add_handler(CommandHandler(['start'], start))


# Handle puzzle command
async def puzzle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    connection = sqlite3.connect(db_path)
    message = update.message

    logger.info(('Command execution:', message.from_user.id, 'puzzle')) # type: ignore

    await command_init.init(ml, connection, message) # type: ignore
    await command_puzzle.puzzle(ml, connection, message) # type: ignore
app.add_handler(CommandHandler(['puzzle', 'p'], puzzle))

# Handle me command
async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    connection = sqlite3.connect(db_path)
    message = update.message

    logger.info(('Command execution:', message.from_user.id, 'me')) # type: ignore
    
    await command_init.init(ml, connection, message) # type: ignore
    await command_me.me(ml, connection, message) # type: ignore
app.add_handler(CommandHandler(['me'], me))


# Handle top command
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    connection = sqlite3.connect(db_path)
    message = update.message

    logger.info(('Command execution:', message.from_user.id, 'top')) # type: ignore
    
    await command_init.init(ml, connection, message) # type: ignore
    await command_top.top(ml, connection, message) # type: ignore
app.add_handler(CommandHandler(['top'], top))


# Handle hardest command
async def hardest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    connection = sqlite3.connect(db_path)
    message = update.message

    logger.info(('Command execution:', message.from_user.id, 'hardest')) # type: ignore
    
    await command_init.init(ml, connection, message) # type: ignore
    await command_hardest.hardest(ml, connection, message) # type: ignore
app.add_handler(CommandHandler(['hardest'], hardest))


# Handle preferences command
async def preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    connection = sqlite3.connect(db_path)
    message = update.message

    logger.info(('Command execution:', message.from_user.id, 'preferences')) # type: ignore
    
    await command_init.init(ml, connection, message) # type: ignore
    await command_preferences.preferences(ml, connection, message) # type: ignore
app.add_handler(CommandHandler(['preferences'], preferences))


# Handle button clicks
async def callback_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    connection = sqlite3.connect(db_path)

    query = update.callback_query
    message = query.message # type: ignore
    logger.info(('Button execution:', query.from_user.id, query.data)) # type: ignore
    
    await command_init.init(ml, connection, message) # type: ignore

    if 'Switch to puzzle' in query.data: # type: ignore
        await command_puzzle.select_puzzle_handler(ml, connection, query) # type: ignore

    elif 'Make move' in query.data: # type: ignore
        await command_puzzle.make_move_puzzle_handler(ml, connection, query) # type: ignore

    elif 'preferences_rating_difference' in query.data: # type: ignore
        await command_preferences.update_rating_difference(ml, connection, query)

    elif 'puzzle vote' in query.data: # type: ignore
        vote = ml.PuzzleVote.PuzzleVote(
            ml, sqlite3.connect(db_path), 
            userId=query.from_user.id, 
            puzzleId=int(query.data.split(':')[1])
        )
        vote.another_vote(float(query.data.split(':')[2])) 

    await query.answer() # type: ignore
app.add_handler(CallbackQueryHandler(callback_inline))

app.run_polling(3)