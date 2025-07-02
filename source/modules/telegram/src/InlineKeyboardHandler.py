from __future__ import annotations
from typing import List, Callable, Any

from telegram import Update, CallbackQuery
from telegram.ext import ContextTypes

handlers: List[InlineKeyboardHandler] = []

class InlineKeyboardHandler:
    def __init__(self):
        self.string = ''
    
    async def __call__(self, data: str, query: CallbackQuery):
        await query.answer()

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
        
        handler.__call__ = wrapper
        return handler
    
    return decorator


def inline_keyboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    for h in handlers:
        if h.string in query.data: # type: ignore
            return h(query.data, query) # type: ignore
        



def add_inline_keyboard_handler(h: InlineKeyboardHandler):
    handlers.append(h)
    