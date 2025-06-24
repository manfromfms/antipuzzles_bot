from ..Puzzle import *
from ..Solution import *

import chess.variant

# This function is required. The name must be the same throughout all the different categories.
# A tuple of two numbers has to be returned: amounts of upvotes and downvotes
def generate_category(puzzle: Puzzle, solution: Solution) -> tuple[float, float]:
    board = chess.variant.AntichessBoard(puzzle.fen)

    for move in solution.moves.split(' '):
        move = chess.Move.from_uci(move)

        if 'x' in board.san(move) and board.piece_at(move.to_square) is None:
            return (10, 0)
        
        board.push(move)

    return (0, 10)
