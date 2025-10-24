"""
This module handles "/daily" command for telegram bot.

Module requirements:
- telegram
- permissions
- daily
- translation
"""

import time
from telegram import Message
from telegram.ext import CommandHandler

from ..users import User
from ..permissions import *
from ..daily_extension import Daily
from ..translation import Translation
from ..telegram import command, add_handler

@command('daily', [], h='Show your daily challenges.')
async def daily(message: Message, params: dict) -> None:
    user = User.searchById(message.from_user.id)
    daily = Daily.searchByUserId(user.id)

    if daily.currentDayFinishTimestamp == 0 or time.time() > daily.currentDayFinishTimestamp:
        daily.update_general()
        daily.update_database_entry()

    await message.chat.send_message(daily.compile().translate(message.from_user.language_code), parse_mode='markdown')

add_handler(CommandHandler(['daily', 'd'], daily))


def command_daily_init():
    SUPERADMIN.addRule('CommandInteraction:daily', True)
    ADMIN     .addRule('CommandInteraction:daily', True)
    DEFAULT   .addRule('CommandInteraction:daily', True)
    RESTRICTED.addRule('CommandInteraction:daily', False)
    BANNED    .addRule('CommandInteraction:daily', False)
