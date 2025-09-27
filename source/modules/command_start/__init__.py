"""
This module handles "/start" command for telegram bot.

Module requirements:
- telegram
- permissions
- user
- translation
"""

from telegram import Message
from telegram.ext import CommandHandler

from ..users import User
from ..daily import Daily
from ..permissions import *
from ..translation import Translation
from ..telegram import command, add_handler

@command('start', [], h='Initial command.')
async def start(message: Message, params: dict) -> None:
    await message.chat.send_message(Translation("Welcome to our bot with antichess puzzles! To see all the available commands execute /help or jump right into solving puzzles using /puzzle (/p works as well)!").translate(message.from_user.language_code))

    if User.searchById(message.from_user.id).id != 0:
        return

    user = User()
    user.id = message.from_user.id
    user.nickname = message.from_user.full_name
    user.pgroup = 1000

    user.update_database_entry()

add_handler(CommandHandler(['start'], start))


def command_start_init():
    SUPERADMIN.addRule('CommandInteraction:start', True)
    ADMIN     .addRule('CommandInteraction:start', True)
    DEFAULT   .addRule('CommandInteraction:start', True)
    RESTRICTED.addRule('CommandInteraction:start', True)
    BANNED    .addRule('CommandInteraction:start', True)
