from src.cls.Puzzle import *
from src.cls.Solution import *

import chess.variant

# This function is required. The name must be the same throughout all the different categories.
# A tuple of two numbers has to be returned: amounts of upvotes and downvotes
def generate_category(puzzle: Puzzle, solution: Solution) -> tuple[float, float]:
    board = chess.variant.AntichessBoard(puzzle.fen)

    all_pieces = board.piece_map().values()
    total_pieces = len(all_pieces)
    
    queens = min(
        sum(1 for piece in all_pieces if piece.piece_type == chess.QUEEN and piece.color == chess.WHITE),
        sum(1 for piece in all_pieces if piece.piece_type == chess.QUEEN and piece.color == chess.BLACK)
    )*0.9
    rooks = min(
        sum(1 for piece in all_pieces if piece.piece_type == chess.ROOK and piece.color == chess.WHITE),
        sum(1 for piece in all_pieces if piece.piece_type == chess.ROOK and piece.color == chess.BLACK)
    )*0.7
    
    # Here each queen gives one upvote where each missing piece gives 0.15 downvotes
    return (32-total_pieces)*0.4, (queens+rooks)
