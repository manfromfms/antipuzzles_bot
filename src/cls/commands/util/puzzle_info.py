import sqlite3 

from src.cls.commands.util.get_themes import *
from src.cls.commands.util.languages import Language

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.cls.Puzzle import Puzzle
    from src.ModuleLoader import ModuleLoader

def complile_puzzle_info(ml: 'ModuleLoader', connection: sqlite3.Connection, puzzle: 'Puzzle', lang: Language, full=False):
    game = puzzle.load_game()

    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM played WHERE puzzleId = ?;', (puzzle.id,))
    count = cursor.fetchone()[0]

    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM played WHERE puzzleId = ? AND elochange >= 0;', (puzzle.id,))
    success = cursor.fetchone()[0]

    vote = ml.PuzzleVote.get_puzzle_votes(puzzle)
    
    s = f'''
🧩 *{lang.translations['Puzzle']} id:{puzzle.id}*

📊 *{lang.translations['Rating']}:*  `{int(puzzle.elo)}±{int(puzzle.elodev)}`
👥 *{lang.translations['Solved']}:*  {success}/{count}
⚔️ *{lang.translations['Game']}:*  {'*' if game.Result.split('-')[0] == '1' else ''}[{game.White}]{'*' if game.Result.split('-')[0] == '1' else ''} vs {'*' if game.Result.split('-')[1] == '1' else ''}[{game.Black}]{'*' if game.Result.split('-')[1] == '1' else ''}
📖 *{lang.translations['Opening']}:* {puzzle.opening.name + f' ({puzzle.openingId})' if puzzle.openingId != 0 else 'Без дебюта'}
🔗 *{lang.translations['Popularity']}:* {int(vote*10)/10}
'''
    
    if full:
        themes = get_themes(ml, connection, puzzle)

        s += f'''\n🔎 *{lang.translations['Themes']}:*'''

        for theme in themes:
            if theme[1] < 0:
                break

            s += f'\n    {theme[0]}: `{int(theme[1]*10)/10}`'

    return s