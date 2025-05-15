import chess.pgn
import chess

import sqlite3

from src.ModuleLoader import *
ml = ModuleLoader()

def find_positions(game: chess.pgn.Game, connection: sqlite3.Connection) -> list[dict]:
    """This function loops through the game and finds potential puzzles before adding them into the database"""
    cursor = connection.cursor()

    positions = []

    h = game.headers
    
    while game is not None:
        # Lichess kindly provides this comment for some positions which the generator should look after
        if 'Lost forced checkmate sequence' in game.comment:

            # Check if the position was already analysed
            cursor.execute('SELECT * FROM positions WHERE fen=?', (game.parent.board().fen(),)) # type: ignore
            if len(cursor.fetchall()) > 1:
                continue

            g = ml.Game.Game(ml, connection)
            g.loadFromHeaders(h)

            p = ml.Puzzle.Puzzle(ml, connection)
            p.update_game_parent(g)

            p.opening = (ml.Opening.Opening(ml, connection)).get_opening(game.parent) # type: ignore # Get the opening for a position and save it into the puzzle 
            p.openingId = p.opening.id

            p.loadFromBoard(game.parent.board()) # type: ignore # Load the puzzle from current board state

            positions.append(p)

        game = game.next() # type: ignore

    return positions
