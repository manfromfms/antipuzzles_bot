"""
This module handles "top" command for telegram bot.

Module requirements:
- telegram
- permissions
- translation
- users
- puzzles
"""

from telegram import Message
from telegram.ext import CommandHandler

from ..permissions import *
from ..users_data import User
from ..translation import Translation
from ..database import get_connection
from ..telegram import command, add_handler


@command(
    n='top', 
    params_spec=[], 
    h='Show top players and your neighbours.'
)
async def top(message: Message, params):
    connection = get_connection()

    user = User.searchById(id=message.from_user.id)
    group = BasicGroup.get(user.pgroup)

    if not group.hasPermission('CommandInteraction:top'):
        await message.chat.send_message((Translation('Access denied') + ' (CommandInteraction:top)').translate(message.from_user.language_code))

    cursor = connection.cursor()
    cursor.execute('''
        SELECT 
            u.id,
            u.nickname,
            ud.elo,
            ud.elodev,
            ROW_NUMBER() OVER (ORDER BY ud.elo DESC) as rank
        FROM users u
        JOIN user_data ud ON ud.userId = u.id
        WHERE ud.elo != 1000
        ORDER BY ud.elo DESC;
    ''')
    data = cursor.fetchall()

    medals = ['🥇', '🥈', '🥉']

    s = '''*---------------- ✨ ''' + Translation('TOP') + ''' 5 ✨ ----------------*\n'''

    # Display top 5 users
    for i in range(5):
        s += f'''
{medals[i] + ' ' if i < len(medals) else str(i+1) + ') '}*{data[i][1]}*
    ''' + Translation('Raiting') + f''': `{int(data[i][2])}±{int(data[i][3])}`
    ''' + Translation('Solved puzzles') + f''': `{(User.searchById(id=data[i][0])).count_solved_puzzles()}`
'''

    if not group.hasPermission('CommandInteraction:top:ViewNeighbours'):
        return s
        
    u = [tup for tup in data if tup[0] == user.id][0]
    
    # If the user is ranked 6th
    if u[4] == 6:
        s += f'''
{str(u[4]) + ') '}*{data[u[4]-1][1]}*
    ''' + Translation('Raiting') + f''': `{int(data[u[4]-1][2])}±{int(data[u[4]-1][3])}`
    ''' + Translation('Solved puzzles') + f''': `{(User.searchById(id=data[u[4]-1][0])).count_solved_puzzles()}`
'''
        if u[4] < len(data):
            s += f'''
{str(u[4]+1) + ') '}*{data[u[4]][1]}*
    ''' + Translation('Raiting') + f''': `{int(data[u[4]][2])}±{int(data[u[4]][3])}`
    ''' + Translation('Solved puzzles') + f''': `{(User.searchById(id=data[u[4]][0])).count_solved_puzzles()}`
'''

    elif u[4] > 6:
        s += '''\n*---------- 🔗 ''' + Translation('YOUR Raiting') + ''' 🔗 ----------*\n'''

        s += f'''
{str(u[4]-1) + ') '}*{data[u[4]-2][1]}*
    ''' + Translation('Raiting') + f''': `{int(data[u[4]-2][2])}±{int(data[u[4]-2][3])}`
    ''' + Translation('Solved puzzles') + f''': `{(User.searchById(id=data[u[4]-2][0])).count_solved_puzzles()}`
'''
        
        s += f'''
{str(u[4]) + ') '}*{data[u[4]-1][1]}*
    ''' + Translation('Raiting') + f''': `{int(data[u[4]-1][2])}±{int(data[u[4]-1][3])}`
    ''' + Translation('Solved puzzles') + f''': `{(User.searchById(id=data[u[4]-1][0])).count_solved_puzzles()}`
'''
        
        if u[4] < len(data):
            s += f'''
{str(u[4]+1) + ') '}*{data[u[4]][1]}*
    ''' + Translation('Raiting') + f''': `{int(data[u[4]][2])}±{int(data[u[4]][3])}`
    ''' + Translation('Solved puzzles') + f''': `{(User.searchById(id=data[u[4]][0])).count_solved_puzzles()}`
'''

    await message.chat.send_message(s.translate(message.from_user.language_code), parse_mode='markdown')


def command_top_init():
    SUPERADMIN.addRule('CommandInteraction:top', True)
    ADMIN     .addRule('CommandInteraction:top', True)
    DEFAULT   .addRule('CommandInteraction:top', True)
    RESTRICTED.addRule('CommandInteraction:top', True)
    BANNED    .addRule('CommandInteraction:top', True)


    SUPERADMIN.addRule('CommandInteraction:top:ViewNeighbours', True)
    ADMIN     .addRule('CommandInteraction:top:ViewNeighbours', True)
    DEFAULT   .addRule('CommandInteraction:top:ViewNeighbours', True)
    RESTRICTED.addRule('CommandInteraction:top:ViewNeighbours', False)
    BANNED    .addRule('CommandInteraction:top:ViewNeighbours', False)


add_handler(CommandHandler(['top', 't'], top))