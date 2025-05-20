from typing import TYPE_CHECKING

import telegram
from io import BytesIO

if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader
    from src.cls.User import User
    from src.cls.Puzzle import Puzzle

import sqlite3

from wand.image import Image

import chess.svg
import chess.variant

import numpy as np

from src.cls.commands.util.convert_args import *
from src.cls.commands.util.puzzle_info import complile_puzzle_info
from src.cls.commands.util.move_to_emoji import convert_move_to_emoji
from src.cls.commands.util.rating_calc import calculate_rating_changes


async def select_puzzle_handler(ml: 'ModuleLoader', connection: sqlite3.Connection, query: telegram.InlineQuery):
    message = query.message
    user = ml.User.User(ml, connection, searchById=message.from_user.id) # type: ignore
    user.select_another_puzzle(int(message.data.split(':')[1])) # type: ignore

    await show_current_puzzle_state(ml, connection, message, user)


def update_ratings(connection: sqlite3.Connection, user: 'User', puzzle: 'Puzzle', userWon):
    cursor = connection.cursor()

    cursor.execute('''SELECT EXISTS(
        SELECT 1 
        FROM played 
        WHERE userId = ? AND puzzleId = ?
    );''', (user.id, puzzle.id))

    if cursor.fetchone()[0] == 1:
        return 0

    results = calculate_rating_changes(
        user.elo,
        user.elodev,
        user.volatility,

        puzzle.elo,
        puzzle.elodev,
        puzzle.volatility,

        1 if userWon else 0
    )

    dif = results[0] - user.elo

    user.elo = results[0]
    user.elodev = results[1]
    user.volatility = results[2]

    puzzle.elo = results[3]
    puzzle.elodev = results[4]
    puzzle.volatility = results[5]

    user.update_database_entry()
    puzzle.update_database_entry()

    cursor.execute('INSERT INTO played (userId, puzzleId, won) VALUES (?, ?, ?)', (user.id, puzzle.id, 1 if userWon else 0))

    connection.commit()
    return dif


async def make_move_puzzle_handler(ml: 'ModuleLoader', connection: sqlite3.Connection, query: telegram.InlineQuery):
    message: telegram.Message = query.message
    user = ml.User.User(ml, connection, searchById=query.from_user.id)
    solution = ml.Solution.Solution(ml, connection, ml.Puzzle.Puzzle(ml, connection), searchByPuzzleId=user.current_puzzle)

    user_move = query.data.split(':')[3] # type: ignore
    solution_moves = solution.moves.split(' ')

    check_current_puzzle = query.data.split(':')[1] # type: ignore
    check_current_puzzle_move = query.data.split(':')[2] # type: ignore


    if user.current_puzzle_move != int(check_current_puzzle_move):
        await message.chat.send_message('Это уже старая позиция! Возможно стоит запросить позицию заново: /puzzle')
        return
    

    if user.current_puzzle != int(check_current_puzzle):
        await message.chat.send_message('Это уже старая позиция! Возможно стоит запросить позицию заново: /puzzle')
        return
    

    if user.current_puzzle_move*2 >= len(solution_moves):
        await message.chat.send_message('Возникла неопознанная ошибка! Выбираем следующую задачу.')

        user.puzzle_selection_policy()
        await show_current_puzzle_state(ml, connection, message, user)

    if solution_moves[user.current_puzzle_move*2] == user_move:
        # Move was correct
        user.current_puzzle_move += 1
        user.update_database_entry()

        if user.current_puzzle_move*2 >= len(solution_moves):
            # TODO: Puzzle solved correctly
            puzzle = ml.Puzzle.Puzzle(ml, connection, searchById=user.current_puzzle)
            dif = int(update_ratings(connection, user, puzzle, True))

            await message.chat.send_message(f'✅ Верно!\n\nИзменение рейтинга: {('' if dif <= 0 else '+') + str(dif)}\nНовый рейтинг: {int(user.elo)}±{int(user.elodev)}\n\nПонравилась ли вам задача? (В процессе)')

            user.puzzle_selection_policy()
            await show_current_puzzle_state(ml, connection, message, user)

            return

        await show_current_puzzle_state(ml, connection, message, user)

    else:
        # TODO: Puzzle solved incorrecly (any incorrect move)
        puzzle = ml.Puzzle.Puzzle(ml, connection, searchById=user.current_puzzle)
        dif = int(update_ratings(connection, user, puzzle, False))
        
        await message.chat.send_message(f'❌ Ошибка! Правильный ход: {solution_moves[user.current_puzzle_move*2]}\n\nИзменение рейтинга: {('' if dif <= 0 else '+') + str(dif)}\nНовый рейтинг: {int(user.elo)}±{int(user.elodev)}\n\nПонравилась ли вам задача? (В процессе)')

        user.puzzle_selection_policy()
        await show_current_puzzle_state(ml, connection, message, user)



async def show_current_puzzle_state(ml: 'ModuleLoader', connection: sqlite3.Connection, message: telegram.Message, user: 'User'):
    puzzle = ml.Puzzle.Puzzle(ml, connection, searchById=user.current_puzzle)
    solution = ml.Solution.Solution(ml, connection, puzzle, searchByPuzzleId=puzzle.id) # type: ignore

    board = chess.variant.AntichessBoard(puzzle.fen)
    solution_moves = solution.moves.split(' ')

    for i in range(user.current_puzzle_move):
        if i*2 >= len(solution_moves)-1:
            return

        board.push_uci(solution_moves[2*i])
        board.push_uci(solution_moves[2*i+1])

    lastmove = chess.Move.from_uci(solution_moves[user.current_puzzle_move*2-1]) if user.current_puzzle_move > 0 else None

    svg = chess.svg.board(board, flipped=not chess.variant.AntichessBoard(puzzle.fen).turn, lastmove=lastmove) # type: ignore
        
    with Image(blob=svg.encode('utf-8'), format="svg") as img:
        img.format = "png"
        png_bytes = img.make_blob()

    buffer = BytesIO(png_bytes) # type: ignore

    rows = [[]]
    for move in board.legal_moves:
        emoji = convert_move_to_emoji(move, board)
        button = telegram.InlineKeyboardButton(text=emoji + board.san(move), callback_data=f"Make move:{puzzle.id}:{user.current_puzzle_move}:{move.uci()}")
        if len(rows[-1]) == 3:
            rows.append([])

        rows[-1].append(button)

    keyboard = telegram.InlineKeyboardMarkup(rows)         
               
    # Send PNG image
    await message.chat.send_photo(buffer, caption='Найдите лучший ход в позиции', reply_markup=keyboard)


async def puzzle(ml: 'ModuleLoader', connection: sqlite3.Connection, message: telegram.Message):
    if message.text is None:
        await message.chat.send_message('Отсутствует текст сообщения')
    
    args = convert_args(message.text) # type: ignore

    if 'id' in args:
        puzzle = ml.Puzzle.Puzzle(ml, connection, searchById=args['id'])

        if puzzle.id == 0:
            await message.chat.send_message('Задача не найдена')
            return

        svg = chess.svg.board(chess.variant.AntichessBoard(puzzle.fen), flipped=not chess.variant.AntichessBoard(puzzle.fen).turn) 
        
        with Image(blob=svg.encode('utf-8'), format="svg") as img:
            img.format = "png"
            png_bytes = img.make_blob()

        buffer = BytesIO(png_bytes) # type: ignore

        button1 = telegram.InlineKeyboardButton(text="Решить задачу", callback_data=f"Switch to puzzle:{puzzle.id}")
        keyboard = telegram.InlineKeyboardMarkup([[button1]])    
        
        # Send PNG image
        await message.chat.send_photo(buffer, caption=complile_puzzle_info(connection, puzzle), reply_markup=keyboard)

    else:
        await message.chat.send_message('Вот ваша текущая задача')

        user = ml.User.User(ml, connection, searchById=message.from_user.id) # type: ignore
        await show_current_puzzle_state(ml, connection, message, user=user) # type: ignore
