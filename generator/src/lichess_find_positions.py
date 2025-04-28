import chess.pgn
import chess

import sqlite3

from src.cls.Game import Game
from src.cls.Puzzle import Puzzle
from src.cls.Opening import Opening, get_opening

def find_positions(game: chess.pgn.Game, connection: sqlite3.Connection) -> list[dict]:
    positions = []

    h = game.headers
    
    while game is not None:
        if 'Lost forced checkmate sequence' in game.comment:
            g = Game(connection)
            g.loadFromHeaders(h)

            p = Puzzle(connection)
            p.update_game_parent(g)

            p.opening = get_opening(game.parent, connection)
            p.openingId = p.opening.id

            p.loadFromBoard(game.parent.board())

            positions.append(p)

        game = game.next()

    return positions
