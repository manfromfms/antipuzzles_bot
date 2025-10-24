"""
This module handles "/theme" command for telegram bot.

Module requirements:
- telegram
- permissions
- translation
- preferences
"""

import telegram
from telegram.ext import CommandHandler
from telegram import Message, CallbackQuery

from ..users import User
from ..permissions import *
from ..daily_extension import Daily
from ..translation import Translation
from ..preferences import Preferences
from ..telegram import command, add_handler, create_inline_keyboard_handler


@create_inline_keyboard_handler(string='preference_selection_theme')
async def preference_selection_theme(data: str, query: CallbackQuery):
    message: telegram.Message = query.message # type: ignore

    user = User.searchById(id=query.from_user.id)
    group = BasicGroup.get(user.pgroup)

    if not group.hasPermission('CommandInteraction:ThemeSelection'):
        return
    
    pref = Preferences.selectByUserId(user.id)

    pref.set_preferences(0, query.data.split(':')[1])

    await message.chat.send_message(Translation('The theme was successfuly switched! This changes will effect after the current puzzle is attempted.').translate(language=message.from_user.language_code))


@command('theme', [], h='Select or deselect current theme.')
async def theme(message: Message, params: dict) -> None:
    user = User.searchById(message.from_user.id)
    daily = Daily.searchByUserId(user.id)
    group = BasicGroup().get(user.pgroup)

    if not group.hasPermission('CommandInteraction:ThemeSelection'):
        return

    buttons = [[]]

    buttons[0].append(telegram.InlineKeyboardButton((Translation('Deselect')).translate(language=message.from_user.language_code), callback_data=f"preference_selection_theme:0"))
    buttons.append([])

    themes = [
        Translation('Opening'), 
        Translation('Middlegame'), 
        Translation('Endgame'),
        Translation('Zugzwang'),
        Translation('Cleaning'),
        Translation('Queen Race'),
        Translation('Promotion'),
        Translation('En Passant'),
    ]

    for i in range(len(themes)):
        theme = themes[i]
        if len(buttons[-1]) < 2:
            buttons[-1].append(telegram.InlineKeyboardButton(theme.translate(language=message.from_user.language_code), callback_data=f"preference_selection_theme:{i + 1}"))
        
        if len(buttons[-1]) == 2:
            buttons.append([])
    
    keyboard = telegram.InlineKeyboardMarkup(buttons)
    
    await message.chat.send_message(Translation('Select the theme you would like to explore!').translate(language=message.from_user.language_code), reply_markup=keyboard)

add_handler(CommandHandler(['theme'], theme))


def command_theme_init():
    SUPERADMIN.addRule('CommandInteraction:ThemeSelection', True)
    ADMIN     .addRule('CommandInteraction:ThemeSelection', True)
    DEFAULT   .addRule('CommandInteraction:ThemeSelection', True)
    RESTRICTED.addRule('CommandInteraction:ThemeSelection', False)
    BANNED    .addRule('CommandInteraction:ThemeSelection', False)
