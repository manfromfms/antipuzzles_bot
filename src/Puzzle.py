import chess.variant


class Puzzle:
    def __init__(self):
        # Link to the game
        self.Site = ''

        # Player's elo
        self.WhiteElo = 0
        self.BlackElo = 0

        # Player's names
        self.White = ''
        self.Black = ''

        # Time control
        self.TimeControl = ''

        # Initial position of a puzzle
        self.position = chess.variant.AntichessBoard()

        # Moves before the puzzle, solution moves and stockfish continuation
        self.movesBefore = []
        self.movesPuzzle = []
        self.movesAfter = []

        # Full list of moves
        self.movesAll = []
