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
            0 if (theme.opening_upvotes + theme.opening_downvotes) == 0 else (theme.opening_upvotes - theme.opening_downvotes) / (theme.opening_upvotes + theme.opening_downvotes),
        ],
        [
            'Миттельшпиль',
            0 if (theme.middlegame_upvotes + theme.middlegame_downvotes) == 0 else (theme.middlegame_upvotes - theme.middlegame_downvotes) / (theme.middlegame_upvotes + theme.middlegame_downvotes),
        ],
        [
            'Эндшпль',
            0 if (theme.endgame_upvotes + theme.endgame_downvotes) == 0 else (theme.endgame_upvotes - theme.endgame_downvotes) / (theme.endgame_upvotes + theme.endgame_downvotes),
        ],
        [
            'Цугцванг',
            0 if (theme.zugzwang_upvotes + theme.zugzwang_downvotes) == 0 else (theme.zugzwang_upvotes - theme.zugzwang_downvotes) / (theme.zugzwang_upvotes + theme.zugzwang_downvotes),
        ],
        [
            'Зачистка',
            0 if (theme.cleaning_upvotes + theme.cleaning_downvotes) == 0 else (theme.cleaning_upvotes - theme.cleaning_downvotes) / (theme.cleaning_upvotes + theme.cleaning_downvotes),
        ],
        [
            'Queen Race',
            0 if (theme.queenrace_upvotes + theme.queenrace_downvotes) == 0 else (theme.queenrace_upvotes - theme.queenrace_downvotes) / (theme.queenrace_upvotes + theme.queenrace_downvotes),
        ],
        [
            'Превращение пешки',
            0 if (theme.promotion_upvotes + theme.promotion_downvotes) == 0 else (theme.promotion_upvotes - theme.promotion_downvotes) / (theme.promotion_upvotes + theme.promotion_downvotes),
        ],
    ]

    return sorted(themes, key=lambda x: x[1], reverse=True)