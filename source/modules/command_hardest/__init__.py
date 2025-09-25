"""
This module handles "hardest" command for telegram bot.

Module requirements:
- telegram
- users_data
- permissions
- translation
- database
- command_puzzle (indirect)
"""

import telegram
from telegram.ext import CommandHandler

from ..permissions import *
from ..users_data import User
from ..translation import Translation
from ..database import get_connection
from ..telegram import command, add_handler


@command(
    n='hardest', 
    params_spec=[
        {'name': 'full', 'type': bool, 'required': False, 'help': 'Without this flag all attempted puzzles will be hidden.'}
    ], 
    h='Show hardest puzzles.'
)
async def hardest(message: telegram.Message, params):
    connection = get_connection()

    user = User.searchById(id=message.from_user.id) # type: ignore
    group = BasicGroup.get(user.pgroup)

    if not group.hasPermission('CommandInteraction:hardest'):
        return
    
    cursor = connection.cursor()

    cursor.execute('''
        SELECT * FROM puzzles 
        WHERE id NOT IN 
            (SELECT puzzleId FROM played WHERE userId = ?) 
        ORDER BY elo DESC 
        LIMIT 6
    ''', (user.id,))

    data = cursor.fetchall()

    buttons = [[]]

    s = '🔥 ' + Translation('The *hardest* puzzles') + ' 🔥\n'

    for puzzle in data:
        buttons[-1].append(
            telegram.InlineKeyboardButton(f'{puzzle[0]}: {int(puzzle[2])}±{int(puzzle[3])}', callback_data=f"switch_to_puzzle:{puzzle[0]} ")
        )

        if len(buttons[-1]) >= 3:
            buttons.append([])

        cursor.execute('SELECT count(*) FROM played WHERE puzzleId = ?', (puzzle[0],))
        count = cursor.fetchone()[0]

        cursor.execute('SELECT count(*) FROM played WHERE puzzleId = ? AND won = 1', (puzzle[0],))
        success = cursor.fetchone()[0]

        s += f'''
🧩 id: `{puzzle[0]}`
    👥 ''' + Translation('Solved') + f''': `{success}/{count}`
    📊 ''' + Translation('Raiting') + f''': `{int(puzzle[2])}±{int(puzzle[3])}`
'''

    keyboard = telegram.InlineKeyboardMarkup(buttons)

    await message.chat.send_message(s.translate(message.from_user.language_code), reply_markup=keyboard, parse_mode='markdown')
add_handler(CommandHandler(['hardest'], hardest))


def command_hardest_init():
    SUPERADMIN.addRule('CommandInteraction:hardest', True)
    ADMIN     .addRule('CommandInteraction:hardest', True)
    DEFAULT   .addRule('CommandInteraction:hardest', True)
    RESTRICTED.addRule('CommandInteraction:hardest', True)
    BANNED    .addRule('CommandInteraction:hardest', True)