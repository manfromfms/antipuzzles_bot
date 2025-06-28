"""
This module handles "help" command for telegram bot. This function should be called after all the commands are set.

Module requirements:
- telegram
"""

from telegram import Message
from telegram.ext import CommandHandler

from ..telegram import command, add_handler, get_handlers, CommandDecorator
from ..users import User
from ..permissions import *
from ..translation import Translation

@command(
    n='help', 
    params_spec=[
        {'name': 'name', 'type': str, 'required': False, 'help': 'Select a command to view information about.'}
    ], 
    h='Display information about a command'
)
async def help(message: Message, params):
    user = User().searchById(message.from_user.id)
    group = BasicGroup().get(user.pgroup)

    if not group.hasPermission(f'CommandInteraction:help'):
        return

    if params['name'] is not None and group.hasPermission(f'CommandInteraction:help:Param:name'):
        for h in get_handlers()[0]:
            handler: CommandDecorator = h.callback
            if handler.name == params['name']:
                if group.hasPermission(f'CommandInteraction:{params['name']}'):
                    return await message.chat.send_message(handler.help.translate(language=message.from_user.language_code), parse_mode='markdown')
                    # TODO: check permissions for each parameter.

        return await message.chat.send_message(Translation('Command not found 🙌').translate(language=message.from_user.language_code), parse_mode='markdown')

    else:
        text = ''
        for h in get_handlers()[0]:
            handler: CommandDecorator = h.callback

            if group.hasPermission(f'CommandInteraction:{handler.name}'):
                text += f'*/{handler.name}*: {handler.h.translate(language=message.from_user.language_code)}\n'

        if len(text) != 0:
            return await message.chat.send_message(text, parse_mode='markdown')
        
    await message.chat.send_message(Translation("Nothing to show here 🫥").translate(language=message.from_user.language_code), parse_mode='markdown')


add_handler(CommandHandler(['help'], help))


def command_help_init():
    SUPERADMIN.addRule('CommandInteraction:help', True)
    ADMIN     .addRule('CommandInteraction:help', True)
    DEFAULT   .addRule('CommandInteraction:help', True)
    RESTRICTED.addRule('CommandInteraction:help', True)
    BANNED    .addRule('CommandInteraction:help', True)


    SUPERADMIN.addRule('CommandInteraction:help:Param:name', True)
    ADMIN     .addRule('CommandInteraction:help:Param:name', True)
    DEFAULT   .addRule('CommandInteraction:help:Param:name', True)
    RESTRICTED.addRule('CommandInteraction:help:Param:name', True)
    BANNED    .addRule('CommandInteraction:help:Param:name', True)