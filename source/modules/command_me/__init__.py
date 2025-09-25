"""
This module handles "me" command for telegram bot.

Module requirements:
- telegram
- users_data
- permissions
- translation
"""

import io
import time
import numpy as np
from telegram import Message
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from telegram.ext import CommandHandler

from ..permissions import *
from ..users_data import User
from ..translation import Translation
from ..database import get_connection
from ..telegram import command, add_handler, get_handlers, CommandDecorator

from .src.get_user_performance import get_themes_performance

@command(
    n='me', 
    params_spec=[{
        'name': 'id', 'type': int, 'required': False, 'help': 'Show information about another user.'
    }], 
    h='Displays your progress.'
)
async def me(message: Message, params):
    user = User().searchById(message.from_user.id)
    group = BasicGroup().get(user.pgroup)

    if not group.hasPermission(f'CommandInteraction:me'):
        return
    
    targetUser = user
    if params['id'] is not None and group.hasPermission(f'CommandInteraction:me:Param:id'):
        targetUser = User().searchById(params['id'])

    # Start the timer
    start_time = time.time()

    connection = get_connection()
    # Get all puzzles with elochange != 0
    cursor = connection.cursor()

    cursor.execute('SELECT count(*) FROM played WHERE userId=?', (targetUser.id,))
    countall = cursor.fetchone()[0]

    cursor.execute('SELECT count(*) FROM played WHERE userId=? AND won = 1', (targetUser.id,))
    countpositive = cursor.fetchone()[0]

    if countall < 5:
        await message.reply_text('Сначала стоит решить несколько задач!')

        return

    cursor.execute('SELECT elochange FROM played WHERE userId=? AND elochange!=0', (targetUser.id,))

    # Convert to array of elo
    changes = [i[0] for i in cursor.fetchall()]
    changes.reverse()

    elo = [targetUser.elo]

    for c in changes:
        elo.append(elo[-1] - c)

    elo.reverse()


    # Approximate a poly
    poly = lambda x, a, b, c: a + b*x + c*x**2

    x = np.array(list(range(max(len(elo)+1-50, 1), len(elo)+1)))
    popt, _ = curve_fit(poly, x, elo[max(len(elo)-50, 0):len(elo)])


    # Draw an ELO plot
    fig1, ax1 = plt.subplots()
    ax1.plot(list(range(1, len(elo)+1)), elo)
    end_time = time.time()
    elapsed_ms = round((end_time - start_time) * 1000)
    ax1.set_ylabel(Translation('Raiting').translate(message.from_user.language_code))
    ax1.set_xlabel(Translation('Puzzles solved (@antipuzzles_bot)').translate(message.from_user.language_code))
    ax1.set_title((Translation('Raiting graph for') + f' {targetUser.nickname}').translate(message.from_user.language_code))
    ax1.grid()


    # Convert the plot
    buf1 = io.BytesIO()
    plt.savefig(buf1, format='png')
    buf1.seek(0)


    # Draw wind rose for each theme
    fig2, ax2 = plt.subplots(subplot_kw=dict(polar=True))
    data = get_themes_performance(connection, targetUser)
    data = [[e[0].translate(message.from_user.language_code), e[1]] for e in data]
    ax2.set_title(Translation('Avg elo change for each theme (@antipuzzles_bot)').translate(message.from_user.language_code))

    names = [d[0] for d in data]
    values = [d[1] for d in data]

    ax2.bar(np.linspace(0, 2*np.pi, len(names)+1)[0:-1], values, tick_label=names)

    # Convert the plot
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png')
    buf2.seek(0)


    # Send additional data

    await message.chat.send_photo(buf2)

    await message.chat.send_photo(buf1, caption=(f'📊 *' + Translation('Raiting') + f'*: `{int(targetUser.elo)}±{int(targetUser.elodev)}`\n🧮 *' + Translation('Solved correctly') + f'*: `{countpositive}/{countall} ({int(countpositive/countall*100)}%)`\n'+ Translation('Elo change rate') + f': {int(10*(popt[1] + 2*popt[2]*x[-1]))/10} elo/' + Translation('Puzzle') + f'\n' + Translation('Plot built in') + f' {elapsed_ms}' + Translation('ms')).translate(message.from_user.language_code), parse_mode='markdown')

    

add_handler(CommandHandler(['me'], me))


def command_me_init():
    SUPERADMIN.addRule('CommandInteraction:me', True)
    ADMIN     .addRule('CommandInteraction:me', True)
    DEFAULT   .addRule('CommandInteraction:me', True)
    RESTRICTED.addRule('CommandInteraction:me', True)
    BANNED    .addRule('CommandInteraction:me', False)

    SUPERADMIN.addRule('CommandInteraction:me:Param:id', True)
    ADMIN     .addRule('CommandInteraction:me:Param:id', True)
    DEFAULT   .addRule('CommandInteraction:me:Param:id', False)
    RESTRICTED.addRule('CommandInteraction:me:Param:id', False)
    BANNED    .addRule('CommandInteraction:me:Param:id', False)