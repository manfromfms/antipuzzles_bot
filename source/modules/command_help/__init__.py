"""
This module handles "help" command for telegram bot. This function should be called after all the commands are set.

Module requirements:
- telegram
"""

from telegram import Message

from ..telegram import command, add_handler, CommandHandler, get_handlers

@command(
    n='help', 
    params_spec=[
        {'name': 'name', 'type': str, 'required': False, 'help': 'Select a command to view information about.'}
    ], 
    h='Display information about a command'
)
async def help(message: Message, params):
    if params['name'] is not None:
        for handler in get_handlers()[0]:
            handler = handler.callback
            if handler.name == params['name']:
                await message.chat.send_message(handler.help, parse_mode='markdown')

    else:
        text = ''
        for handler in get_handlers()[0]:
            handler = handler.callback

            text += f'*/{handler.name}*: {handler.h}\n'


        await message.chat.send_message(text, parse_mode='markdown')

add_handler(CommandHandler(['help'], help))