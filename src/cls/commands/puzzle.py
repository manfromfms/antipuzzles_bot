from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader
    from src.cls.User import User
    from src.cls.Puzzle import Puzzle

import sqlite3

import telebot
from telebot import types

from wand.image import Image

import chess.svg
import chess.variant

import numpy as np

from src.cls.commands.util.convert_args import *
from src.cls.commands.util.puzzle_info import complile_puzzle_info
from src.cls.commands.util.move_to_emoji import convert_move_to_emoji
from src.cls.commands.util.rating_calc import calculate_rating_changes


def select_puzzle_handler(ml: 'ModuleLoader', connection: sqlite3.Connection, bot: telebot.TeleBot, call: telebot.types.CallbackQuery):
    user = ml.User.User(ml, connection, searchById=call.from_user.id)
    user.select_another_puzzle(int(call.data.split(':')[1])) # type: ignore

    show_current_puzzle_state(ml, connection, bot, call.message.chat, user)


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


def make_move_puzzle_handler(ml: 'ModuleLoader', connection: sqlite3.Connection, bot: telebot.TeleBot, call: telebot.types.CallbackQuery):
    user = ml.User.User(ml, connection, searchById=call.from_user.id)
    solution = ml.Solution.Solution(ml, connection, ml.Puzzle.Puzzle(ml, connection), searchByPuzzleId=user.current_puzzle) # type: ignore

    user_move = call.data.split(':')[3] # type: ignore
    solution_moves = solution.moves.split(' ')

    check_current_puzzle = call.data.split(':')[1] # type: ignore
    check_current_puzzle_move = call.data.split(':')[2] # type: ignore


    if user.current_puzzle_move != int(check_current_puzzle_move):
        bot.send_message(call.message.chat.id, 'Это уже старая позиция! Возможно стоит запросить позицию заново: /puzzle')
        return
    

    if user.current_puzzle != int(check_current_puzzle):
        bot.send_message(call.message.chat.id, 'Это уже старая позиция! Возможно стоит запросить позицию заново: /puzzle')
        return
    

    if user.current_puzzle_move*2 >= len(solution_moves):
        bot.send_message(call.message.chat.id, 'Возникла неопознанная ошибка! Выбираем следующую задачу.')

        user.puzzle_selection_policy()
        show_current_puzzle_state(ml, connection, bot, call.message.chat, user)

    if solution_moves[user.current_puzzle_move*2] == user_move:
        # Move was correct
        user.current_puzzle_move += 1
        user.update_database_entry()

        if user.current_puzzle_move*2 >= len(solution_moves):
            # TODO: Puzzle solved correctly
            puzzle = ml.Puzzle.Puzzle(ml, connection, searchById=user.current_puzzle)
            dif = int(update_ratings(connection, user, puzzle, True))

            try: # This sometimes would give an error
                bot.send_message(call.message.chat.id, str('Информация о задаче:\n\n'+complile_puzzle_info(connection, puzzle)))
            except:
                pass

            bot.send_message(call.message.chat.id, f'✅ Верно!\n\nИзменение рейтинга: {('' if dif <= 0 else '+') + str(dif)}\nНовый рейтинг: {int(user.elo)}±{int(user.elodev)}\n\nПонравилась ли вам задача? (В процессе)')

            user.puzzle_selection_policy()
            show_current_puzzle_state(ml, connection, bot, call.message.chat, user)

            return

        show_current_puzzle_state(ml, connection, bot, call.message.chat, user)

    else:
        # TODO: Puzzle solved incorrecly (any incorrect move)
        puzzle = ml.Puzzle.Puzzle(ml, connection, searchById=user.current_puzzle)
        dif = int(update_ratings(connection, user, puzzle, False))

        try: # This sometimes would give an error
            bot.send_message(call.message.chat.id, str('Информация о задаче:\n\n'+complile_puzzle_info(connection, puzzle)))
        except():
            pass
        
        bot.send_message(call.message.chat.id, f'❌ Ошибка! Правильный ход: {solution_moves[user.current_puzzle_move*2]}\n\nИзменение рейтинга: {('' if dif <= 0 else '+') + str(dif)}\nНовый рейтинг: {int(user.elo)}±{int(user.elodev)}\n\nПонравилась ли вам задача? (В процессе)')

        user.puzzle_selection_policy()
        show_current_puzzle_state(ml, connection, bot, call.message.chat, user)



def show_current_puzzle_state(ml: 'ModuleLoader', connection: sqlite3.Connection, bot: telebot.TeleBot, chat: telebot.types.Chat, user: 'User'):
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

    rows = [[]]
    for move in board.legal_moves:
        emoji = convert_move_to_emoji(move, board)
        button = types.InlineKeyboardButton(text=emoji + board.san(move), callback_data=f"Make move:{puzzle.id}:{user.current_puzzle_move}:{move.uci()}")
        if len(rows[-1]) == 3:
            rows.append([])

        rows[-1].append(button)

    keyboard = types.InlineKeyboardMarkup(rows)         
               
    
    # Send PNG image
    bot.send_photo(chat.id, png_bytes, caption='Найдите лучший ход в позиции', reply_markup=keyboard)


def puzzle(ml: 'ModuleLoader', connection: sqlite3.Connection, bot: telebot.TeleBot, message: telebot.types.Message):
    if message.text is None:
        bot.send_message(message.chat.id, 'Отсутствует текст сообщения')
    
    args = convert_args(telebot.util.extract_arguments(message.text)) # type: ignore
    print(args)

    if 'id' in args:
        puzzle = ml.Puzzle.Puzzle(ml, connection, searchById=args['id'])

        if puzzle.id == 0:
            bot.send_message(message.chat.id, 'Задача не найдена')
            return

        svg = chess.svg.board(chess.variant.AntichessBoard(puzzle.fen), flipped=not chess.variant.AntichessBoard(puzzle.fen).turn) 
        
        with Image(blob=svg.encode('utf-8'), format="svg") as img:
            img.format = "png"
            png_bytes = img.make_blob()

        keyboard = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text="Решить задачу", callback_data=f"Switch to puzzle:{puzzle.id}")
        keyboard.add(button1)       
        
        # Send PNG image
        bot.send_photo(message.chat.id, png_bytes, caption=complile_puzzle_info(connection, puzzle), reply_markup=keyboard)

    else:
        bot.send_message(message.chat.id, 'Вот ваша текущая задача')

        user = ml.User.User(ml, connection, searchById=message.from_user.id) # type: ignore
        show_current_puzzle_state(ml, connection, bot, chat=message.chat, user=user) # type: ignore
