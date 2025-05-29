from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader

import sqlite3
import telegram
import matplotlib.pyplot as plt
import io
import time

import numpy
from scipy.optimize import curve_fit
import numpy as np

async def me(ml: 'ModuleLoader', connection: sqlite3.Connection, message: telegram.Message):
    user = ml.User.User(ml, connection, searchById=message.from_user.id) # type: ignore

    # Start the timer
    start_time = time.time()

    # Get all puzzles with elochange != 0
    cursor = connection.cursor()
    cursor.execute('SELECT elochange FROM played WHERE userId=? AND elochange!=0', (user.id,))

    # Convert to array of elo
    changes = [i[0] for i in cursor.fetchall()]
    changes.reverse()

    elo = [user.elo]

    for c in changes:
        elo.append(elo[-1] - c)

    elo.reverse()

    # Approximate a poly
    poly = lambda x, a, b, c: a + b*x + c*x**2

    x = np.array(list(range(max(len(elo)+1-50, 1), len(elo)+1)))
    popt, _ = curve_fit(poly, x, elo[max(len(elo)-50, 1):len(elo)])
    y = poly(x, popt[0], popt[1], popt[2])

    # Draw a plot
    fig, ax = plt.subplots()

    ax.plot(list(range(1, len(elo)+1)), elo)

    end_time = time.time()
    elapsed_ms = round((end_time - start_time) * 1000)

    ax.set_ylabel('Рейтинг')
    ax.set_xlabel('Решено задач (@antipuzzles_bot)')

    ax.set_title(f'Динамика рейтинга игрока {user.nickname}')

    # ax.plot(x, y)

    ax.grid()

    # Send the plot
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Send additional data
    cursor.execute('SELECT count(*) FROM played WHERE userId=?', (user.id,))
    count = cursor.fetchone()[0]

    await message.chat.send_photo(buf, caption=f'📊 *Рейтинг*: `{int(user.elo)}±{int(user.elodev)}`\n🧮 *Решено задач*: `{count}`\nДинамика рейтинга: {int(10*(popt[1] + 2*popt[2]*x[-1]))/10} elo/задача\nГрафик построен за {elapsed_ms}мс', parse_mode='markdown')
