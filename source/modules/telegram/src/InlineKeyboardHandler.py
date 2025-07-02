from __future__ import annotations
from typing import List, Callable, Any

import logging

from telegram import Update, CallbackQuery
from telegram.ext import ContextTypes

handlers: List[InlineKeyboardHandler] = []


async def simple_function(data: str, query: CallbackQuery):
    return await query.answer()


class InlineKeyboardHandler:
    def __init__(self):
        self.string = ''

        self.call = simple_function
    
    async def __call__(self, data: str, query: CallbackQuery):
        return await self.call(data, query)

def create_inline_keyboard_handler(string: str = '') -> Callable[..., InlineKeyboardHandler]:
    """
    Creates a decorator that returns an instance of InlineKeyboardHandler
    with the specified string value and replaces its __call__ method.
    
    Args:
        string: Custom string value for the handler
        
    Returns:
        A decorator function that creates an InlineKeyboardHandler instance
    """
    def decorator(func: Callable[[str, CallbackQuery], Any]) -> InlineKeyboardHandler:
        # Create handler instance
        handler = InlineKeyboardHandler()
        
        # Set custom string if provided
        handler.string = string
        
        # Replace __call__ method with the decorated function
        async def wrapper(data: str, query: CallbackQuery):
            return await func(data, query)
        
        handler.call = wrapper
        handlers.append(handler)
        return handler
    
    return decorator


async def inline_keyboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    logging.info((query.from_user.id, query.message.chat.id, query.data))

    for h in handlers:
        if h.string in query.data: # type: ignore
            print(h.string, query.data, True)
            return await h(query.data, query) # type: ignore
