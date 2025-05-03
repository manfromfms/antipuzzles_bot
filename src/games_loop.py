import src.lichess_find_positions as find
import chess.pgn
import chess

import sqlite3

def loop_through_games(path: str, connection: sqlite3.Connection) -> list[dict]:
    pgn = open(path, encoding="utf-8")
    game = chess.pgn.read_game(pgn)

    positions = []

    while game is not None:
        positions.extend(find.find_positions(game, connection))
        game = chess.pgn.read_game(pgn)
    
    return positions
