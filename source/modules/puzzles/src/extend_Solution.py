from .Solution import Solution as Solution_lite
from .Theme import Theme

import chess.engine
from chess.engine import Mate, Cp
import chess.variant
import chess.engine

class Solution(Solution_lite):
    def generate(self):
        if len(self.get_puzzle().fen) < 1:
            self.remove_puzzle()
            return
        
        self.cursor.execute('INSERT INTO positions (fen) VALUES (?) ON CONFLICT DO NOTHING', (self.get_puzzle().fen,))
        self.connection.commit()
        
        board = chess.variant.AntichessBoard(self.get_puzzle().fen)
        engine = chess.engine.SimpleEngine.popen_uci(os.getenv('ffish_path')) # type: ignore

        print(board.fen())

        #engine.configure({'Threads': os.getenv('ffish_Threads'), 'Hash': os.getenv('ffish_Hash')})
        engine.configure({'Threads': 1, 'Hash': 64})

        # 2 seconds for initial analysis
        info = engine.analyse(board, chess.engine.Limit(time=2))

        # If the mate was found for current player, then do the analysis
        if info['score'].pov(board.turn) > Mate(100): # type: ignore
            result = self.recursive_analysis(board, engine)

            if result[2] > 1:
                self.moves = ' '.join([m_.uci() for m_ in result[0]])
                self.fish_solution = self.moves + ' ' + ' '.join([m_.uci() for m_ in result[1]])
                self.length = result[2]

                self.update_database_entry()

                Theme().generate(self.get_puzzle(), self)

                self.get_puzzle().isProcessed = True
                self.get_puzzle().update_database_entry()
            else:
                self.remove_puzzle()
        else: 
            print("Failed to find the solution")
            self.remove_puzzle()

        engine.close()
