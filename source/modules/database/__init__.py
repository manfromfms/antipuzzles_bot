"""
Database interraction is done using this module
==================

This module provides full access to the database, as well as some useful classes related to users and puzzles.
Use `db_init` before accessing the database.

Module requirements:
- None
"""

import sqlite3

from .src.database import db_init, get_connection
from .src.Game import Game
from .src.Opening import Opening
from .src.Preferences import Preferences
from .src.Puzzle import Puzzle
from .src.PuzzleVote import PuzzleVote
from .src.extend_Solution import Solution
from .src.Theme import Theme
from .src.User import User

from pathlib import Path

def init(path: str | Path) -> sqlite3.Connection | None:
    """Generate db file or use existing one. Also sets up the db structure for all classes presented in this module.

    Args:
        path (str | Path): Path to a db file. (Local path is counted from the main python file)

    Returns:
        sqlite3.Connection: Connection to a db.
    """

    db_init(path)

    Game.setup_database_structure()
    Opening.setup_database_structure()
    Preferences.setup_database_structure()
    Puzzle.setup_database_structure()
    Puzzle.setup_database_structure_positions()
    Puzzle.setup_database_structure_telegramImageId()
    PuzzleVote.setup_database_structure()
    Solution.setup_database_structure()
    Theme.setup_database_structure()
    User.setup_database_structure()

    return get_connection()
