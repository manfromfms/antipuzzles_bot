# TODO: Write docstring

from typing import TYPE_CHECKING

import sqlite3
import telegram
import chess.svg
import chess.variant
from io import BytesIO
from wand.image import Image

from telegram import Message, CallbackQuery
from telegram.ext import CommandHandler

from ..permissions import *
from ..users_data import User
from ..daily_extension import Daily
from ..database import get_connection
from ..translation import Translation
from ..preferences import Preferences
from ..puzzles import Puzzle, Solution
from ..telegram import command, add_handler, create_inline_keyboard_handler

from .src.rating_calc import calculate_rating_changes
from .src.compile_puzzle_info import complile_puzzle_info
from .src.show_current_puzzle_state import show_current_puzzle_state


def update_ratings(user: User, puzzle: Puzzle, userWon):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('''SELECT EXISTS(
        SELECT 1 s
        FROM played 
        WHERE userId = ? AND puzzleId = ?
    );''', (user.id, puzzle.id))

    if cursor.fetchone()[0] == 1:
        return 0
    
    preferences = Preferences.selectByUserId(user.id)

    results = calculate_rating_changes(
        user.elo,
        user.elodev,
        user.volatility,

        puzzle.elo,
        puzzle.elodev,
        puzzle.volatility,

        1 if userWon else 0,
        1 if preferences.get_preferences()[0] == '0' or preferences.get_preferences()[0] == '' else 0.5
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

    cursor.execute('INSERT INTO played (userId, puzzleId, won, elochange) VALUES (?, ?, ?, ?)', (user.id, puzzle.id, 1 if userWon else 0, dif))

    connection.commit()
    return dif


@command(
    n='puzzle', 
    params_spec=[
        {'name': 'id', 'type': int, 'required': False, 'help': 'Select a puzzle to show information about.'}
    ], 
    h='Show current position or information about a puzzle.'
)
async def puzzle(message: Message, params):
    user = User.searchById(message.from_user.id)
    group = BasicGroup.get(user.pgroup)
    
    if not group.hasPermission('CommandInteraction:puzzle'):
        return


    if params['id'] is not None and group.hasPermission('CommandInteraction:puzzle:Param:id'):
        puzzle = Puzzle.searchById(id=params['id'])

        if puzzle.id == 0:
            return await message.chat.send_message(Translation('No such puzzle').translate(message.from_user.language_code)) # type: ignore

        svg = chess.svg.board(chess.variant.AntichessBoard(puzzle.fen), flipped=not chess.variant.AntichessBoard(puzzle.fen).turn) 
        
        with Image(blob=svg.encode('utf-8'), format="svg") as img:
            img.format = "png"
            png_bytes = img.make_blob()

        buffer = BytesIO(png_bytes) # type: ignore

        button1 = telegram.InlineKeyboardButton(text=Translation("Challenge!").translate(message.from_user.language_code), callback_data=f"switch_to_puzzle:{puzzle.id}") # type: ignore
        keyboard = telegram.InlineKeyboardMarkup([[button1]])
        
        # Send PNG image
        await message.chat.send_photo(buffer, caption=complile_puzzle_info(puzzle).translate(message.from_user.language_code), reply_markup=keyboard, parse_mode=telegram.constants.ParseMode('Markdown')) # type: ignore

    else:
        puzzle = Puzzle.searchById(user.current_puzzle)

        await message.chat.send_message(Translation('Here is your current puzzle.').translate(message.from_user.language_code)) # type: ignore

        await message.chat.send_message(complile_puzzle_info(puzzle).translate(message.from_user.language_code), parse_mode=telegram.constants.ParseMode('Markdown')) # type: ignore
        await show_current_puzzle_state(message, user=user) # type: ignore

add_handler(CommandHandler(['puzzle', 'p'], puzzle))


@create_inline_keyboard_handler(string='switch_to_puzzle')
async def select_puzzle_handler(data: str, query: CallbackQuery):
    message = query.message # type: ignore
    user = User.searchById(id=query.from_user.id) # type: ignore
    user.select_another_puzzle(int(query.data.split(':')[1])) # type: ignore

    await show_current_puzzle_state(message, user=user) # type: ignore


@create_inline_keyboard_handler(string='make_move')
async def make_move_puzzle_handler(data: str, query: CallbackQuery):
    message: telegram.Message = query.message # type: ignore

    user = User.searchById(id=query.from_user.id)
    solution = Solution.searchByPuzzleId(puzzleId=user.current_puzzle)
    group = BasicGroup.get(user.pgroup)

    user_move = query.data.split(':')[3] # type: ignore
    solution_moves = solution.moves.split(' ')

    check_current_puzzle = query.data.split(':')[1] # type: ignore
    check_current_puzzle_move = query.data.split(':')[2] # type: ignore

    if not group.hasPermission('ButtonInteraction:make_move'):
        return await message.chat.send_message(Translation('You don\'t have access to puzzle solving.').translate(query.from_user.language_code)) # type: ignore


    if user.current_puzzle_move != int(check_current_puzzle_move):
        return await message.chat.send_message(Translation('This is an old position. Try executing /puzzle to get your current position.').translate(query.from_user.language_code)) # type: ignore
    

    if user.current_puzzle != int(check_current_puzzle):
        return await message.chat.send_message(Translation('This is an old puzzle. Try executing /puzzle to get your current puzzle.').translate(query.from_user.language_code)) # type: ignore
    

    if user.current_puzzle_move*2 >= len(solution_moves):
        await message.chat.send_message(Translation('Unexpected error occured. Selecting another puzzle.').translate(query.from_user.language_code)) # type: ignore

        user.puzzle_selection_policy()
        return await show_current_puzzle_state(message, user)
    

    if solution_moves[user.current_puzzle_move*2] == user_move:
        # Move was correct
        user.current_puzzle_move += 1
        user.update_database_entry()

        if user.current_puzzle_move*2 >= len(solution_moves):
            # Puzzle successfuly finished
            puzzle =Puzzle.searchById(id=user.current_puzzle)

            if group.hasPermission('ButtonInteraction:make_move:rated_puzzle_solving'):
                dif = int(update_ratings(user, puzzle, True))
                
                # Update daily challenges
                Daily.searchByUserId(user.id).update_general()
                state = Daily.searchByUserId(user.id).update_state(dif)

                if state > 0:
                    await message.chat.send_message(('🏁 *' + Translation('DAILY CHALLENGE IS COMPLETED') + '* 🏁\n_' + Translation('Don\'t forget to come back tomorrow!') + '_').translate(query.from_user.language_code), parse_mode='markdown')
            else:
                dif = 0
            user.puzzle_selection_policy()

            buttons = [[
                telegram.InlineKeyboardButton('🟩', callback_data=f'puzzle_vote:{puzzle.id}:1'),
                telegram.InlineKeyboardButton('🟥', callback_data=f'puzzle_vote:{puzzle.id}:-1'),
            ]]

            await message.chat.send_message(complile_puzzle_info(puzzle, level=1).translate(query.from_user.language_code), parse_mode=telegram.constants.ParseMode('Markdown')) # type: ignore

            await message.chat.send_message((f'✅ *' + Translation('Correct!') + '*\n\n📈 ' + Translation('Elo change') + f': {(('' if dif < 0 else '+') if dif != 0 else '±') + str(dif)}\n📊 ' + Translation('New raiting') + f': {int(user.elo)}±{int(user.elodev)}\n🖥️ ' + Translation('Analysis') + f': [lichess](https://lichess.org/analysis/antichess/{puzzle.fen.replace(' ', '%20')})\n\n' + Translation('Did you like this puzzle?')).translate(query.from_user.language_code), reply_markup=telegram.InlineKeyboardMarkup(buttons), parse_mode='markdown') # type: ignore

            return await show_current_puzzle_state(message, user)

        return await show_current_puzzle_state(message, user)

    else:
        # Wrong move = puzzle failed

        # Lost against the puzzle
        puzzle = Puzzle.searchById(id=user.current_puzzle)
        if group.hasPermission('ButtonInteraction:make_move:rated_puzzle_solving'):
            dif = int(update_ratings(user, puzzle, False))
                
            # Update daily challenges
            Daily.searchByUserId(user.id).update_general()
            state = Daily.searchByUserId(user.id).update_state(dif)

            if state > 0:
                await message.chat.send_message(('🏁 *' + Translation('DAILY CHALLENGE IS COMPLETED') + '* 🏁\n_' + Translation('Don\'t forget to come back tomorrow!') + '_').translate(query.from_user.language_code), parse_mode='markdown')
        else:
            dif = 0
        user.puzzle_selection_policy()

        # Add vote buttons
        buttons = [[
            telegram.InlineKeyboardButton('🟩', callback_data=f'puzzle_vote:{puzzle.id}:0.1'),
            telegram.InlineKeyboardButton('🟥', callback_data=f'puzzle_vote:{puzzle.id}:-0.1'),
        ]]
        
        # Send messages
        await message.chat.send_message(complile_puzzle_info(puzzle).translate(query.from_user.language_code), parse_mode=telegram.constants.ParseMode('Markdown')) # type: ignore

        await message.chat.send_message((f'❌ *' + Translation('Wrong!') + '* ' + Translation('Correct move') + f': *{solution_moves[int(check_current_puzzle_move)*2]}*\n\n📈 ' + Translation('Elo change') + f': {(('' if dif < 0 else '+') if dif != 0 else '±') + str(dif)}\n📊 ' + Translation('New raiting') + f': {int(user.elo)}±{int(user.elodev)}\n🖥️ ' + Translation('Analysis') + f': [lichess](https://lichess.org/analysis/antichess/{puzzle.fen.replace(' ', '%20')})\n\n' + Translation('Did you like this puzzle?')).translate(query.from_user.language_code), reply_markup=telegram.InlineKeyboardMarkup(buttons), parse_mode='markdown') # type: ignore

        await show_current_puzzle_state(message, user)


def command_puzzle_init():
    SUPERADMIN.addRule('CommandInteraction:puzzle', True)
    ADMIN     .addRule('CommandInteraction:puzzle', True)
    DEFAULT   .addRule('CommandInteraction:puzzle', True)
    RESTRICTED.addRule('CommandInteraction:puzzle', True)
    BANNED    .addRule('CommandInteraction:puzzle', False)


    SUPERADMIN.addRule('CommandInteraction:puzzle:Param:id', True)
    ADMIN     .addRule('CommandInteraction:puzzle:Param:id', True)
    DEFAULT   .addRule('CommandInteraction:puzzle:Param:id', True)
    RESTRICTED.addRule('CommandInteraction:puzzle:Param:id', True)
    BANNED    .addRule('CommandInteraction:puzzle:Param:id', False)


    SUPERADMIN.addRule('ButtonInteraction:make_move', True)
    ADMIN     .addRule('ButtonInteraction:make_move', True)
    DEFAULT   .addRule('ButtonInteraction:make_move', True)
    RESTRICTED.addRule('ButtonInteraction:make_move', True)
    BANNED    .addRule('ButtonInteraction:make_move', False)


    SUPERADMIN.addRule('ButtonInteraction:make_move:rated_puzzle_solving', True)
    ADMIN     .addRule('ButtonInteraction:make_move:rated_puzzle_solving', True)
    DEFAULT   .addRule('ButtonInteraction:make_move:rated_puzzle_solving', True)
    RESTRICTED.addRule('ButtonInteraction:make_move:rated_puzzle_solving', False)
    BANNED    .addRule('ButtonInteraction:make_move:rated_puzzle_solving', False)
