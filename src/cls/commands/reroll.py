from typing import TYPE_CHECKING

import telegram
from io import BytesIO

if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader
    from src.cls.User import User
    from src.cls.Puzzle import Puzzle

import sqlite3

import src.cls.commands.puzzle as puzzle


async def reroll(ml: 'ModuleLoader', connection: sqlite3.Connection, message: telegram.Message):
    user = ml.User.User(ml, connection, searchById=message.from_user.id) # type: ignore
    user.puzzle_selection_policy() # type: ignore

    if user.pgroup != 0:
        return

    await puzzle.show_current_puzzle_state(ml, connection, message, user)