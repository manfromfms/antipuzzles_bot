from __future__ import annotations
from typing import List

from telegram import Update, CallbackQuery
from telegram.ext import ContextTypes

handlers: List[InlineKeyboardHandler] = []

class InlineKeyboardHandler:
    string = ''

    async def __call__(self, data: str, query: CallbackQuery):
        await query.answer()


def inline_keyboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    for h in handlers:
        if h.string in query.data: # type: ignore
            return h(query.data, query) # type: ignore


def add_inline_keyboard_handler(h: InlineKeyboardHandler):
    handlers.append(h)
    