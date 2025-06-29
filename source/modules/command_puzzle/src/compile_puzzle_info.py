import sqlite3

from ...puzzles import Puzzle
from ...translation import Translation
from ...database import get_connection

def complile_puzzle_info(puzzle: Puzzle, level=0) -> Translation:
    """Get information about a puzzle as a Translation.

    Args:
        puzzle (Puzzle): Instance of Puzzle to show information about.
        level (int, optional): Level of information (0=basic, 1=after solving, 2=full). Defaults to 0.

    Returns:
        Translation: Puzzle info as translation.
    """

    # TODO: Popularity
    # TODO: Different levels of info

    connection = get_connection()

    game = puzzle.load_game()

    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM played WHERE puzzleId = ?;', (puzzle.id,))
    count = cursor.fetchone()[0]

    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM played WHERE puzzleId = ? AND elochange >= 0;', (puzzle.id,))
    success = cursor.fetchone()[0]

    # vote = ml.PuzzleVote.get_puzzle_votes(puzzle)
    vote = 0
    
    s = f'''🧩 *''' + (Translation('Puzzle')) + f''' id:''' + (puzzle.id) + f'''*\n📊 *''' + (Translation('Rating')) + f''':*  `''' + (int(puzzle.elo)) + f'''±''' + (int(puzzle.elodev)) + f'''`\n👥 *''' + (Translation('Solved')) + f''':*  ''' + (success) + f'''/''' + (count) + f'''\n⚔️ *''' + (Translation('Game')) + f''':*  ''' + ('*' if game.Result.split('-')[0] == '1' else '') + f'''[''' + (game.White) + f''']''' + ('*' if game.Result.split('-')[0] == '1' else '') + f''' vs ''' + ('*' if game.Result.split('-')[1] == '1' else '') + f'''[''' + (game.Black) + f''']''' + ('*' if game.Result.split('-')[1] == '1' else '') + f'''\n📖 *''' + (Translation('Opening')) + f''':* ''' + ((puzzle.getOpening().name) + f' ({puzzle.openingId})' if puzzle.openingId != 0 else Translation('Not specified')) + f'''\n🔗 *''' + (Translation('Popularity')) + f''':* ''' + (int(vote*10)/10)
    
    a='''if full:
        themes = get_themes(ml, connection, puzzle)

        s += f'\n🔎 * + (lang.translations['Themes']) + f:*'

        for theme in themes:
            if theme[1] < 0:
                break

            s += f'\n     + (theme[0]) + f: ` + (int(theme[1]*10)/10) + f`'''

    return s