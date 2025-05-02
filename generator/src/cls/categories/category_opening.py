from src.cls.Puzzle import *
from src.cls.Solution import *

import chess.variant

# This function is required. The name must be the same throughout all the different categories.
# A tuple of two numbers has to be returned: the amount of upvotes and downvotes
def generate_category(puzzle: Puzzle, solution: Solution) -> tuple[int, int]:
    board = chess.variant.AntichessBoard(puzzle.fen)

    all_pieces = board.piece_map().values()
    total_pieces = len(all_pieces)
    
    queens = sum(1 for piece in all_pieces if piece.piece_type == chess.QUEEN)
    
    # Here each queen gives one upvote where each missing piece gives 0.15 downvotes
    return queens, (32-total_pieces)*0.15
