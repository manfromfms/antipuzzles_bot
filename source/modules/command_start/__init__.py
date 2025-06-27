"""
This module handles "start" command for telegram bot.

Module requirements:
- telegram
"""

from telegram import Message
from telegram.ext import CommandHandler

from ..telegram import command, add_handler


@command('start', [], h='Initial command.')
async def start(message: Message, params: dict) -> None:
    await message.chat.send_message('/start')

add_handler(CommandHandler(['start'], start))


def command_start_init():
    pass

