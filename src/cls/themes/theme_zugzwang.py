from src.cls.Puzzle import *
from src.cls.Solution import *

import chess.variant

# This function is required. The name must be the same throughout all the different categories.
# A tuple of two numbers has to be returned: amounts of upvotes and downvotes
def generate_category(puzzle: Puzzle, solution: Solution) -> tuple[float, float]:
    board = chess.variant.AntichessBoard(puzzle.fen)

    moves = solution.moves.split(' ')

    pairs = [moves[i:i+2] for i in range(0, len(moves), 2)]

    for pair in pairs:
        board.push_uci(pair[0])

        move = list(board.legal_moves)[0]

        if not board.is_capture(move):
            return (10, 0)
        
        board.push_uci(pair[1])
        
    return (0, 10)
