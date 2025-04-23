import src.lichess_find_positions as find
import chess.pgn
import chess

import sqlite3

def loop_through_games(path: str, cursor: sqlite3.Cursor) -> list[dict]:
    pgn = open(path, encoding="utf-8")
    game = chess.pgn.read_game(pgn)

    positions = []

    while game is not None:
        positions.extend(find.find_positions(game, cursor))
        game = chess.pgn.read_game(pgn)
    
    return positions
