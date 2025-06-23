from ..Puzzle import *
from ..Solution import *

import chess.variant

# This function is required. The name must be the same throughout all the different categories.
# A tuple of two numbers has to be returned: amounts of upvotes and downvotes
def generate_category(puzzle: Puzzle, solution: Solution) -> tuple[float, float]:
    for move in solution.moves.split(' '):
        move = chess.Move.from_uci(move)

        if move.promotion is not None:
            return (10, 0)

    return (0, 10)
