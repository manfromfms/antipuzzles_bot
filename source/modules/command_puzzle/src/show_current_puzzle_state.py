import telegram
import chess.svg
import chess.variant
from io import BytesIO
from wand.image import Image

from ...users_data import User
from ...database import get_connection
from ...translation import Translation
from ...puzzles import Puzzle, Solution

from .get_file_id import get_file_id, add_file_id
from .move_to_emoji import convert_move_to_emoji

async def show_current_puzzle_state(message: telegram.Message, user: User):
    """Generates and sends puzzle state to a user.

    Args:
        message (telegram.Message): Any message.
        user (User): User class from module (not python-telegram-bot).
    """
    connection = get_connection()

    if user.current_puzzle == 0 or user.current_puzzle is None:
        return await message.reply_text(Translation('It seems that there are no puzzles left for you. Try changing the selection. If this issue continues to appear, text the administrator.').translate(message.from_user.language_code))


    puzzle = Puzzle.searchById(id=user.current_puzzle)
    solution = Solution.searchByPuzzleId(puzzleId=puzzle.id) # type: ignore

    board = chess.variant.AntichessBoard(puzzle.fen)
    solution_moves = solution.moves.split(' ')

    for i in range(user.current_puzzle_move):
        if i*2 >= len(solution_moves)-1:
            return

        board.push_uci(solution_moves[2*i])
        board.push_uci(solution_moves[2*i+1])

    lastmove = chess.Move.from_uci(solution_moves[user.current_puzzle_move*2-1]) if user.current_puzzle_move > 0 else None

    buffer = ''

    # Check if position has file_id in telegram
    file_id = get_file_id(connection, board.fen())
    if file_id is not None:
        buffer = file_id
    else:
        svg = chess.svg.board(board, flipped=not chess.variant.AntichessBoard(puzzle.fen).turn, lastmove=lastmove) # type: ignore
            
        with Image(blob=svg.encode('utf-8'), format="svg") as img:
            img.format = "png"
            png_bytes = img.make_blob()

        buffer = BytesIO(png_bytes) # type: ignore

    rows = [[]]
    for move in board.legal_moves:
        emoji = convert_move_to_emoji(move, board)
        button = telegram.InlineKeyboardButton(text=emoji + board.san(move), callback_data=f"make_move:{puzzle.id}:{user.current_puzzle_move}:{move.uci()}")
        if len(rows[-1]) == (4 if board.legal_moves.count() <= 24 else 5):
            rows.append([])

        rows[-1].append(button)

    keyboard = telegram.InlineKeyboardMarkup(rows)         
               
    # Send PNG image
    msg = await message.chat.send_photo(buffer, caption=f'{'⚪' if board.turn == chess.WHITE else '⬛'} *' + Translation('Find the best move for').translate(message.from_user.language_code) + f' ' + Translation('white' if board.turn == chess.WHITE else 'black').translate(message.from_user.language_code) + f'* {'⬜' if board.turn == chess.WHITE else '⚫'}', reply_markup=keyboard, parse_mode='markdown')

    if file_id is None and len(msg.photo) > 0:
        add_file_id(connection, board.fen(), msg.photo[0].file_id)

    return