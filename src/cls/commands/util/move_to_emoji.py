import chess

def convert_move_to_emoji(move: chess.Move, board: chess.Board) -> str:
    if board.piece_at(move.from_square).symbol() == 'K': # type: ignore
        return '♔'
    
    if board.piece_at(move.from_square).symbol() == 'Q': # type: ignore
        return '♕'
    
    if board.piece_at(move.from_square).symbol() == 'B': # type: ignore
        return '♗'
    
    if board.piece_at(move.from_square).symbol() == 'N': # type: ignore
        return '♘'
    
    if board.piece_at(move.from_square).symbol() == 'P': # type: ignore
        return '♙'
    
    if board.piece_at(move.from_square).symbol() == 'R': # type: ignore
        return '♖'
    
    if board.piece_at(move.from_square).symbol() == 'k': # type: ignore
        return '♚'
    
    if board.piece_at(move.from_square).symbol() == 'q': # type: ignore
        return '♛'
    
    if board.piece_at(move.from_square).symbol() == 'b': # type: ignore
        return '♝'
    
    if board.piece_at(move.from_square).symbol() == 'n': # type: ignore
        return '♞'
    
    if board.piece_at(move.from_square).symbol() == 'p': # type: ignore
        return '♟'
    
    if board.piece_at(move.from_square).symbol() == 'r': # type: ignore
        return '♜'
    
    return ''