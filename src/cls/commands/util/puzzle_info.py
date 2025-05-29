import sqlite3 

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.cls.Puzzle import Puzzle
    from src.ModuleLoader import ModuleLoader

def complile_puzzle_info(ml: 'ModuleLoader', connection: sqlite3.Connection, puzzle: 'Puzzle'):
    game = puzzle.load_game()

    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM played WHERE puzzleId = ?;', (puzzle.id,))
    count = cursor.fetchone()[0]

    vote = ml.PuzzleVote.get_puzzle_votes(puzzle)
    
    s = f'''
ℹ️ *Задача id:{puzzle.id}*

📊 *Рейтинг:*  `{int(puzzle.elo)}±{int(puzzle.elodev)}`
✅ *Решено:*  {count} раз
⚔️ *Партия:*  {'*' if game.Result.split('-')[0] == '1' else ''}[{game.White}]{'*' if game.Result.split('-')[0] == '1' else ''} vs {'*' if game.Result.split('-')[1] == '1' else ''}[{game.Black}]{'*' if game.Result.split('-')[1] == '1' else ''}
📖 *Дебют:* {puzzle.opening.name + f' ({puzzle.openingId})' if puzzle.openingId != 0 else 'Без дебюта'}
🔗 *Оценка:* {int(vote*10)/10}
    '''

    return s