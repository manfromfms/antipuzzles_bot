from ..Puzzle import *
from ..Solution import *

import chess.variant

# This function is required. The name must be the same throughout all the different categories.
# A tuple of two numbers has to be returned: amounts of upvotes and downvotes
def generate_category(puzzle: Puzzle, solution: Solution) -> tuple[float, float]:
    board = chess.variant.AntichessBoard(puzzle.fen)

    player = board.turn

    up = 0
    down = 0

    moves = solution.moves.split(' ')
    for move in moves:
        move = chess.Move.from_uci(move)

        if board.is_capture(move):
            if board.turn == player:
                down += 1.75 # VERY BAD if player has to capture
            else:
                up += 1 # QUITE GOOD that the opponent has to capture

        else:
            if board.turn == player:
                up += 0.1 # OK if player doesn't have to capture
            else:
                down += 1.5 # VERY bad that the opponent doesn's have to capture

        board.push(move)

    fish = solution.fish_solution.split(' ')
    for i in range(len(moves), len(fish)):
        if fish[i] == '':
            break

        move = chess.Move.from_uci(fish[i])

        if move not in list(board.legal_moves):
            break

        if board.is_capture(move):
            if board.turn == player:
                down += 0.08**(i - len(moves) + 1)
            else:
                up += 0.2**(i - len(moves) + 1)

        else:
            if board.turn == player:
                up += 0.03**(i - len(moves) + 1)
            else:
                down += 0.08**(i - len(moves) + 1)

        board.push(move)

    return (up, down)
