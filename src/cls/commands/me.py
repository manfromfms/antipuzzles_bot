from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader

import sqlite3
import telegram
import matplotlib.pyplot as plt
import io
import time

async def me(ml: 'ModuleLoader', connection: sqlite3.Connection, message: telegram.Message):
    user = ml.User.User(ml, connection, searchById=message.from_user.id) # type: ignore

    start_time = time.time()

    cursor = connection.cursor()

    cursor.execute('SELECT elochange FROM played WHERE userId=? AND elochange!=0', (user.id,))

    changes = [i[0] for i in cursor.fetchall()]
    changes.reverse()

    elo = [user.elo]

    for c in changes:
        elo.append(elo[-1] - c)

    elo.reverse()

    fig, ax = plt.subplots()

    ax.plot(list(range(1, len(elo)+1)), elo)

    end_time = time.time()
    elapsed_ms = round((end_time - start_time) * 1000)

    ax.set_ylabel('Рейтинг')
    ax.set_xlabel('Решено задач (@antipuzzles_bot)')

    ax.set_title(f'Динамика рейтинга игрока {user.nickname}')

    ax.grid()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    cursor.execute('SELECT count(*) FROM played WHERE userId=?', (user.id,))
    count = cursor.fetchone()[0]

    await message.chat.send_photo(buf, caption=f'📊 *Рейтинг*: `{int(user.elo)}±{int(user.elodev)}`\n🧮 *Решено задач*: `{count}`\nГрафик построен за {elapsed_ms}мс', parse_mode='markdown')
