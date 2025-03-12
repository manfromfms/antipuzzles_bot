import chess.pgn

from src.Database import Database


class Generator:
    def __init__(self, db):
        self.db = db


    def check_for_existing_eval(self, game=chess.pgn.Game()):
        if game.next() is None:
            return False

        return game.next().eval() is not None


    def generate(self, pgn_io):
        while True:
            game = chess.pgn.read_game(pgn_io)

            if game is None:
                continue

            if not self.check_for_existing_eval(game):
                continue

            print(game.headers['Site'])
