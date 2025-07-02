"""
This module contains telegram-related classes:
None

Module requirements:
None
"""

import os
import logging
from dotenv import load_dotenv
load_dotenv()

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

from .src.command import command, CommandDecorator

from .src.InlineKeyboardHandler import create_inline_keyboard_handler, inline_keyboard_handler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger()

app = ApplicationBuilder()\
    .token((os.getenv('telegram_token')\
    .replace('\\x3a', ':')))\
    .read_timeout(7)\
    .get_updates_read_timeout(42)\
    .build()


app.add_handler(CallbackQueryHandler(inline_keyboard_handler))


def add_handler(handler):
    app.add_handler(handler)


def run_polling():
    app.run_polling()


def get_handlers():
    return app.handlers