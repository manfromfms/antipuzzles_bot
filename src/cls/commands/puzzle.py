from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader

import sqlite3
import telebot
from wand.image import Image

import chess.svg
import chess.variant

from src.cls.commands.util.convert_args import *


def puzzle(ml: 'ModuleLoader', connection: sqlite3.Connection, bot: telebot.TeleBot, message: telebot.types.Message):
    if message.text is None:
        bot.send_message(message.chat.id, 'Отсутствует текст сообщения')
    
    args = convert_args(telebot.util.extract_arguments(message.text)) # type: ignore
    print(args)

    if hasattr(args, 'id'):
        puzzle = ml.Puzzle.Puzzle(ml, connection, searchById=args['id'])

        svg = chess.svg.board(chess.variant.AntichessBoard(puzzle.fen), flipped=not chess.variant.AntichessBoard(puzzle.fen).turn) 
        
        with Image(blob=svg.encode('utf-8'), format="svg") as img:
            img.format = "png"
            png_bytes = img.make_blob()
        
        # Send PNG image
        bot.send_photo(message.chat.id, png_bytes)

    else:
        bot.send_message(message.chat.id, 'Неверный набор параметров')
