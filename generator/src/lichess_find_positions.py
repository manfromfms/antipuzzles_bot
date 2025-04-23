import chess.pgn
import chess

from src.cls.Game import *
from src.cls.Puzzle import *

def find_positions(game: chess.pgn.Game, cursor: sqlite3.Cursor) -> list[dict]:
    positions = []

    h = game.headers
    
    while game is not None:
        if 'Lost forced checkmate sequence' in game.comment:
            g = Game(cursor)
            g.loadFromHeaders(h)

            p = Puzzle(cursor)
            p.loadFromBoard(game.board())

            p.update_game_parent(g)

            positions.append(p)

        game = game.next()

    return positions
