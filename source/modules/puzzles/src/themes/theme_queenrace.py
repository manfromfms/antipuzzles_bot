from ..Puzzle import *
from ..Solution import *

import chess.variant

# This function is required. The name must be the same throughout all the different categories.
# A tuple of two numbers has to be returned: amounts of upvotes and downvotes
def generate_category(puzzle: Puzzle, solution: Solution) -> tuple[float, float]:
    board = chess.variant.AntichessBoard(puzzle.fen)

    up = 0
    down = 0

    for move in solution.moves.split(' '):
        move = chess.Move.from_uci(move)

        if (board.piece_at(move.from_square).piece_type == chess.QUEEN or board.piece_at(move.from_square).piece_type == chess.ROOK) and (board.is_capture(move)):
            up += 1
        else:
            down += 1.5

        board.push(move)

    return up, down
