import sqlite3 

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.cls.Puzzle import Puzzle

def complile_puzzle_info(connection: sqlite3.Connection, puzzle: 'Puzzle'):
    game = puzzle.load_game()

    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM played WHERE puzzleId = ?;', (puzzle.id,))
    count = cursor.fetchone()[0]

    # TODO: оценка задачи 
    s = f'Задача:\n\t{puzzle.id}\n' \
        +f'Рейтинг:\n\t{int(puzzle.elo)}±{int(puzzle.elodev)}\n'\
        +f'Решена:\n\t{count} раз\n'\
        +f'Из партии:\n\t{game.Black} vs. {game.White}'
    
        #+f'Оценка:\n\tIn Progress\n'\

    return s