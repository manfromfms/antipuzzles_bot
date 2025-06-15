from typing import TYPE_CHECKING

import telegram
from io import BytesIO

if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader
    from src.cls.User import User
    from src.cls.Puzzle import Puzzle

import sqlite3
import io
import chess.pgn
from wand.image import Image

import src.cls.commands.puzzle as puzzle

from src.cls.commands.util.convert_args import *
import src.cls.commands.util.get_file_id as tgfid

async def select_opening(ml: 'ModuleLoader', connection: sqlite3.Connection, query: telegram.CallbackQuery):
    user = ml.User.User(ml, connection, searchById=query.from_user.id) # type: ignore
    pref = ml.Preferences.Preferences(ml, connection, searchByUserId=user.id)

    pref.openingId = int(query.data.split(':')[1])
    pref.update_database_entry()

    user.puzzle_selection_policy()

    opening = ml.Opening.Opening(ml, connection, searchById=pref.openingId)

    await query.message.chat.send_message(f'Выбран дебют *{opening.name}* ({opening.id})', parse_mode='markdown')


async def opening(ml: 'ModuleLoader', connection: sqlite3.Connection, message: telegram.Message):
    user = ml.User.User(ml, connection, searchById=message.from_user.id) # type: ignore
    args = convert_args(message.text) # type: ignore

    id = 0

    if 'id' in args:
        id = int(args['id'])

    await opening_true(ml, connection, user, message.chat, id)


async def opening_button(ml: 'ModuleLoader', connection: sqlite3.Connection, query: telegram.CallbackQuery):
    user = ml.User.User(ml, connection, searchById=query.from_user.id) # type: ignore
    
    id = int(query.data.split(':')[1])

    await opening_true(ml, connection, user, query.message.chat, id)


async def opening_true(ml: 'ModuleLoader', connection: sqlite3.Connection, user: 'User', chat: telegram.Chat, id: int):
    opening = ml.Opening.Opening(ml, connection, searchById=id)

    game = chess.pgn.read_game(io.StringIO(f'[Variant "Antichess"]\n\n{opening.sequence}'))
    board = game.end().board()
    
    # Check if position has file_id in telegram
    file_id = tgfid.get_file_id(connection, board.fen())
    if file_id is not None:
        buffer = file_id
    else:
        svg = chess.svg.board(board, flipped=board.turn) # type: ignore
            
        with Image(blob=svg.encode('utf-8'), format="svg") as img:
            img.format = "png"
            png_bytes = img.make_blob()

        buffer = BytesIO(png_bytes) # type: ignore

    children = opening.get_children_class()

    keyboard = []

    if id != 0:
        keyboard.append([
            telegram.InlineKeyboardButton(f'⬆️ Вернуться ⬆️', callback_data=f'show opening:{opening.parentId}'),
        ])

        keyboard.append([
            telegram.InlineKeyboardButton(f'Вырбрать {opening.name} ({opening.id})', callback_data=f'select opening:{opening.id}'),
        ])
            
    keyboard.append([
        telegram.InlineKeyboardButton('❌ Отменить выбор дебюта ❌', callback_data='preferences_remove_opening'),
    ])

    for i in range(len(children)):
        child = children[i]

        keyboard.append([
            telegram.InlineKeyboardButton(f'{child.name} ({child.id})', callback_data=f'show opening:{child.id}'),
        ])

    msg = await chat.send_photo(buffer, caption=f'*{opening.name}* ({opening.id})\nПозиция: `{opening.sequence}`\nВсего задач: `{opening.count_puzzles()}`\nРешенных задач: `{opening.count_puzzles_solved()}`\nРешено вами: `{opening.count_puzzles_solved(userId=user.id)}`', parse_mode='markdown', reply_markup=telegram.InlineKeyboardMarkup(keyboard))
    

    if file_id is None and len(msg.photo) > 0:
        tgfid.add_file_id(connection, board.fen(), msg.photo[0].file_id)