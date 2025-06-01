import sqlite3 


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.cls.Puzzle import Puzzle
    from src.cls.Theme import Theme
    from src.ModuleLoader import ModuleLoader
    from src.cls.User import User


def get_single_theme(cursor: sqlite3.Cursor, theme: str, userId: int):
    if theme not in ['opening', 'middlegame', 'endgame', 'cleaning', 'promotion', 'queenrace', 'zugzwang']:
        return 0

    cursor.execute(f'''
        SELECT 
            played.id,
            played.elochange,
            themes.{theme}_upvotes,
            themes.{theme}_downvotes,
            CAST((themes.{theme}_upvotes - themes.{theme}_downvotes) AS REAL) / 
            NULLIF(themes.{theme}_upvotes + themes.{theme}_downvotes, 0) AS total
        FROM played 
        INNER JOIN themes ON themes.puzzleId = played.puzzleId
        WHERE played.userId = ? 
        AND played.elochange != 0
        AND themes.{theme}_upvotes > themes.{theme}_downvotes
    ''', (userId,)) # This query requires additional awareness

    data = cursor.fetchall()

    data = [(d[0], d[1], d[2], d[3], d[4]) if d[3] != 0 else (d[0], d[1], d[2], d[3], d[4]) for d in data]
    
    elochange = [d[1]*d[4] for d in data]
    total = [d[4] for d in data]

    return sum(elochange) / sum(total)

def get_themes_performance(ml: 'ModuleLoader', connection: sqlite3.Connection, user: 'User'):
    cursor = connection.cursor()

    themes = [
        [
            'Дебют',
            get_single_theme(cursor, 'opening', user.id),
        ],
        [
            'Миттельшпиль',
            get_single_theme(cursor, 'middlegame', user.id),
        ],
        [
            'Эндшпль',
            get_single_theme(cursor, 'endgame', user.id),
        ],
        [
            'Цугцванг',
            get_single_theme(cursor, 'zugzwang', user.id),
        ],
        [
            'Зачистка',
            get_single_theme(cursor, 'cleaning', user.id),
        ],
        [
            'Queen Race',
            get_single_theme(cursor, 'queenrace', user.id),
        ],
        [
            'Превращение пешки',
            get_single_theme(cursor, 'promotion', user.id),
        ],
    ]

    return sorted(themes, key=lambda x: x[1], reverse=True)