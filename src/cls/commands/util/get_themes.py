import sqlite3 

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.cls.Puzzle import Puzzle
    from src.cls.Solution import Solution
    from src.cls.Theme import Theme
    from src.ModuleLoader import ModuleLoader

def get_themes(ml: 'ModuleLoader', connection: sqlite3.Connection, puzzle: 'Puzzle'):
    empty_solution = ml.Solution.Solution(ml, connection, puzzle)

    theme = ml.Theme.Theme(ml, connection, puzzle, empty_solution, searchByPuzzleId=puzzle.id)

    themes = [
        [
            'Дебют',
            (theme.opening_upvotes - theme.opening_downvotes) / (theme.opening_upvotes + theme.opening_downvotes),
        ],
        [
            'Миттельшпиль',
            (theme.middlegame_upvotes - theme.middlegame_downvotes) / (theme.middlegame_upvotes + theme.middlegame_downvotes),
        ],
        [
            'Эндшпль',
            (theme.endgame_upvotes - theme.endgame_downvotes) / (theme.endgame_upvotes + theme.endgame_downvotes),
        ],
        [
            'Цугцванг',
            (theme.zugzwang_upvotes - theme.zugzwang_downvotes) / (theme.zugzwang_upvotes + theme.zugzwang_downvotes),
        ],
    ]

    return sorted(themes, key=lambda x: x[1], reverse=True)