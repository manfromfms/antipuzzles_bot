from typing import TYPE_CHECKING

import telegram
from io import BytesIO

import sqlite3

from wand.image import Image

import chess.svg
import chess.variant

from telegram import Message
from telegram.ext import CommandHandler

from ..telegram import command, add_handler, get_handlers, CommandDecorator
from ..users import User
from ..permissions import *
from ..translation import Translation
from ..puzzles import Puzzle

from .src.compile_puzzle_info import complile_puzzle_info

@command(
    n='puzzle', 
    params_spec=[
        {'name': 'id', 'type': int, 'required': True, 'help': 'Select a puzzle to show information about.'}
    ], 
    h='Show current position or information about a puzzle.'
)
async def puzzle(message: Message, params):
    user = User().searchById(message.from_user.id)
    group = BasicGroup().get(user.pgroup)
    
    if not group.hasPermission('CommandInteraction:puzzle'):
        return


    if 'id' in params and group.hasPermission('CommandInteraction:puzzle:Param:id'):
        puzzle = Puzzle.searchById(id=params['id'])

        if puzzle.id == 0:
            await message.chat.send_message('Задача не найдена')
            return

        svg = chess.svg.board(chess.variant.AntichessBoard(puzzle.fen), flipped=not chess.variant.AntichessBoard(puzzle.fen).turn) 
        
        with Image(blob=svg.encode('utf-8'), format="svg") as img:
            img.format = "png"
            png_bytes = img.make_blob()

        buffer = BytesIO(png_bytes) # type: ignore

        button1 = telegram.InlineKeyboardButton(text=Translation("Challenge!").translate(message.from_user.language_code), callback_data=f"Switch to puzzle:{puzzle.id}")
        keyboard = telegram.InlineKeyboardMarkup([[button1]])    
        
        # Send PNG image
        await message.chat.send_photo(buffer, caption=complile_puzzle_info(puzzle).translate(message.from_user.language_code), reply_markup=keyboard, parse_mode=telegram.constants.ParseMode('Markdown')) # type: ignore

    '''else:
        await message.chat.send_message('Вот ваша текущая задача')

        user = ml.User.User(ml, connection, searchById=message.from_user.id) # type: ignore
        puzzle = ml.Puzzle.Puzzle(ml, connection, searchById=user.current_puzzle)

        await message.chat.send_message(complile_puzzle_info(ml, connection, puzzle, lang=Language(message.from_user.language_code)), parse_mode=telegram.constants.ParseMode('Markdown'))
        await show_current_puzzle_state(ml, connection, message, user=user) # type: ignore'''

add_handler(CommandHandler(['puzzle'], puzzle))


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
