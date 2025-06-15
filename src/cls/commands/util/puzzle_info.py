import sqlite3 

from src.cls.commands.util.get_themes import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.cls.Puzzle import Puzzle
    from src.ModuleLoader import ModuleLoader

def complile_puzzle_info(ml: 'ModuleLoader', connection: sqlite3.Connection, puzzle: 'Puzzle', full=False):
    game = puzzle.load_game()

    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM played WHERE puzzleId = ?;', (puzzle.id,))
    count = cursor.fetchone()[0]

    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM played WHERE puzzleId = ? AND elochange >= 0;', (puzzle.id,))
    success = cursor.fetchone()[0]

    vote = ml.PuzzleVote.get_puzzle_votes(puzzle)
    
    s = f'''
ℹ️ *Задача id:{puzzle.id}*

📊 *Рейтинг:*  `{int(puzzle.elo)}±{int(puzzle.elodev)}`
✅ *Решено:*  {success}/{count}
⚔️ *Партия:*  {'*' if game.Result.split('-')[0] == '1' else ''}[{game.White}]{'*' if game.Result.split('-')[0] == '1' else ''} vs {'*' if game.Result.split('-')[1] == '1' else ''}[{game.Black}]{'*' if game.Result.split('-')[1] == '1' else ''}
📖 *Дебют:* {puzzle.opening.name + f' ({puzzle.openingId})' if puzzle.openingId != 0 else 'Без дебюта'}
🔗 *Оценка:* {int(vote*10)/10}
'''
    
    if full:
        themes = get_themes(ml, connection, puzzle)

        s += '''\n🔎 *Темы:*'''

        for theme in themes:
            if theme[1] < 0:
                break

            s += f'\n    {theme[0]}: `{int(theme[1]*10)/10}`'

    return s