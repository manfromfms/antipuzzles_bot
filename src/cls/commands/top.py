from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader

import sqlite3
import telegram

async def top(ml: 'ModuleLoader', connection: sqlite3.Connection, message: telegram.Message):
    user = ml.User.User(ml, connection, searchById=message.from_user.id) # type: ignore

    cursor = connection.cursor()
    cursor.execute('''
        SELECT id, nickname, elo, elodev,
            ROW_NUMBER() OVER (ORDER BY elo DESC) as rank
        FROM users WHERE elo != 1000
        ORDER BY elo DESC
    ''')
    data = cursor.fetchall()

    medals = ['🥇', '🥈', '🥉']

    s = '''*---------------- ✨ ТОП 5 ✨ ----------------*\n'''

    # Display top 5 users
    for i in range(5):
        s += f'''
{medals[i] + ' ' if i < len(medals) else str(i+1) + ') '}*{data[i][1]}*
    Рейтинг: `{int(data[i][2])}±{int(data[i][3])}`
    Решено задач: `{(ml.User.User(ml, connection, searchById=data[i][0])).count_solved_puzzles()}`
'''
        
    u = [tup for tup in data if tup[0] == user.id][0]
    
    # If the user is ranked 6th
    if u[4] == 6:
        s += f'''
{str(u[4]) + ') '}*{data[u[4]-1][1]}*
    Рейтинг: `{int(data[u[4]-1][2])}±{int(data[u[4]-1][3])}`
    Решено задач: `{(ml.User.User(ml, connection, searchById=data[u[4]-1][0])).count_solved_puzzles()}`
'''
        if u[4] < len(data):
            s += f'''
{str(u[4]+1) + ') '}*{data[u[4]][1]}*
    Рейтинг: `{int(data[u[4]][2])}±{int(data[u[4]][3])}`
    Решено задач: `{(ml.User.User(ml, connection, searchById=data[u[4]][0])).count_solved_puzzles()}`
'''

    elif u[4] > 6:
        s += '''\n*---------- 🔗 ВАШ РЕЙТИНГ 🔗 ----------*\n'''

        s += f'''
{str(u[4]-1) + ') '}*{data[u[4]-2][1]}*
    Рейтинг: `{int(data[u[4]-2][2])}±{int(data[u[4]-2][3])}`
    Решено задач: `{(ml.User.User(ml, connection, searchById=data[u[4]-2][0])).count_solved_puzzles()}`
'''
        
        s += f'''
{str(u[4]) + ') '}*{data[u[4]-1][1]}*
    Рейтинг: `{int(data[u[4]-1][2])}±{int(data[u[4]-1][3])}`
    Решено задач: `{(ml.User.User(ml, connection, searchById=data[u[4]-1][0])).count_solved_puzzles()}`
'''
        
        if u[4] < len(data):
            s += f'''
{str(u[4]+1) + ') '}*{data[u[4]][1]}*
    Рейтинг: `{int(data[u[4]][2])}±{int(data[u[4]][3])}`
    Решено задач: `{(ml.User.User(ml, connection, searchById=data[u[4]][0])).count_solved_puzzles()}`
'''

    await message.chat.send_message(s, parse_mode='markdown')