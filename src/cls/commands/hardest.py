from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader

import sqlite3
import telegram

async def hardest(ml: 'ModuleLoader', connection: sqlite3.Connection, message: telegram.Message):
    user = ml.User.User(ml, connection, searchById=message.from_user.id) # type: ignore
    
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

    for puzzle in data:
        buttons[-1].append(
            telegram.InlineKeyboardButton(f'{puzzle[0]}: {int(puzzle[2])}±{int(puzzle[3])}', callback_data=f"Switch to puzzle:{puzzle[0]} ")
        )

        if len(buttons[-1]) >= 3:
            buttons.append([])

    keyboard = telegram.InlineKeyboardMarkup(buttons)

    await message.chat.send_message('🔥 Самые *сложные* задачи 🔥', reply_markup=keyboard, parse_mode='markdown')