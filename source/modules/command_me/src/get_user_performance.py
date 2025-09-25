import sqlite3 

from ...users_data import User
from ...translation import Translation

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

    return 0 if sum(total) == 0 else sum(elochange) / sum(total)

def get_themes_performance(connection: sqlite3.Connection, user: User):
    cursor = connection.cursor()

    themes = [
        [
            Translation('Opening'),
            get_single_theme(cursor, 'opening', user.id),
        ],
        [
            Translation('Middle game'),
            get_single_theme(cursor, 'middlegame', user.id),
        ],
        [
            Translation('End game'),
            get_single_theme(cursor, 'endgame', user.id),
        ],
        [
            Translation('Zugzwang'),
            get_single_theme(cursor, 'zugzwang', user.id),
        ],
        [
            Translation('Cleaning'),
            get_single_theme(cursor, 'cleaning', user.id),
        ],
        [
            Translation('Queen Race'),
            get_single_theme(cursor, 'queenrace', user.id),
        ],
        [
            Translation('Pawn promotion'),
            get_single_theme(cursor, 'promotion', user.id),
        ],
        [
            Translation('Enpassant'),
            get_single_theme(cursor, 'enpassant', user.id),
        ],
    ]

    return sorted(themes, key=lambda x: x[1], reverse=True)