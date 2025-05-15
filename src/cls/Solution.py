from __future__ import annotations

import sqlite3

import chess.engine
from chess.engine import Mate, Cp
import chess.variant
import chess.engine

import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader
    from src.cls.Puzzle import Puzzle

class Solution:
    def __init__(self, ml: 'ModuleLoader', connection: sqlite3.Connection, puzzle: Puzzle, searchByPuzzleId=0):
            
        self.connection = connection
        self.cursor = connection.cursor()

        self.ml = ml

        self.id = 0
        self.puzzleId = puzzle.id
        self.moves = ''
        self.length = 0
        self.fish_solution = ''

        # Some additional stuff
        self.puzzle = puzzle

        if searchByPuzzleId != 0:
            self.cursor.execute('SELECT * FROM solutions WHERE puzzleId = ? LIMIT 1', (searchByPuzzleId,))
            data = self.cursor.fetchone()

            if data is None:
                return
            
            self.id = data[0]
            self.puzzleId = data[1]
            self.moves = data[2]
            self.length = data[3]
            self.fish_solution = data[4]

            self.puzzle = self.ml.Puzzle.Puzzle(ml, self.connection, searchById=self.puzzleId)


    def generate(self):
        if len(self.puzzle.fen) < 1:
            self.remove_puzzle()
            return
        
        board = chess.variant.AntichessBoard(self.puzzle.fen)
        engine = chess.engine.SimpleEngine.popen_uci(os.getenv('ffish_path')) # type: ignore

        print(board.fen())

        engine.configure({'Hash': os.getenv('ffish_Threads'), 'Hash': os.getenv('ffish_Threads')})

        # 3 seconds for initial analysis
        info = engine.analyse(board, chess.engine.Limit(time=1))

        # If the mate was found for current player, then do the analysis
        if info['score'].pov(board.turn) > Mate(100): # type: ignore
            result = self.recursive_analysis(board, engine)

            if result[2] > 1:
                self.moves = ' '.join([m_.uci() for m_ in result[0]])
                self.fish_solution = self.moves + ' ' + ' '.join([m_.uci() for m_ in result[1]])
                self.length = result[2]

                self.update_database_entry()

                self.ml.Category.Category(self.ml, self.connection, self.puzzle, self).generate()

                self.puzzle.isProcessed = True
                self.puzzle.update_database_entry()
            else:
                self.remove_puzzle()
        else: 
            print("Failed to find the solution")
            self.remove_puzzle()

        engine.close()


    def remove_puzzle(self):
        self.cursor.execute('DELETE FROM puzzles WHERE (id = ?)', (self.puzzleId,))

        self.connection.commit()


    def recursive_analysis(self, board: chess.variant.AntichessBoard, engine: chess.engine.SimpleEngine):
        print('New call')
        moves = get_moves(board)

        # Check if there are no legal moves at all
        if len(moves) == 0:
            print('Stop due to lack of moves for player')
            return [[], [], 0]

        # Check if there is only one possible move
        if len(moves) == 1:
            board.push(moves[0])
            
            # Play the engine move
            if len(get_moves(board)) > 0:
                engine_move = engine.play(board, chess.engine.Limit(time=0.2)).move
                board.push(engine_move) # type: ignore

                result = self.recursive_analysis(board, engine)

                # Undo all the moves and return the result
                board.pop()
                board.pop()

                if len(result[0]) > 0:
                    result[0].insert(0, engine_move)
                    result[0].insert(0, moves[0])

                return result
            else:
                print('Stop due to lack of moves for engine')
                return [moves, [], 0]

        # Now if there are multiple legal moves
        # Do wide analysis of every possible move in current position
        wide_analysis = engine.analyse(board, chess.engine.Limit(time=1.5), multipv=500)

        # If failed to find a solution (might be possible due to limitations of computational time)
        if wide_analysis[0]['score'].pov(board.turn) < Mate(100): # type: ignore
            print('Stop due to lack of solution')
            return [[], [], 0]
        
        # Check the amount of good moves (mate as well as generally better for player)
        # Fairy stockfish sorts all the line by how good they are thus only the second entry has to be checked
        if wide_analysis[1]['score'].pov(board.turn) > Cp(0): # type: ignore
            print('Stop due to multiple possible moves')
            return [[], wide_analysis[0]['pv'], 0] # type: ignore
                
        # Now forward the game for further depth analysis
        correct_move = wide_analysis[0]['pv'][0] # type: ignore
        board.push(correct_move)

        # Play the engine move
        if len(get_moves(board)) > 0:
            engine_move = engine.play(board, chess.engine.Limit(time=0.2)).move
            board.push(engine_move) # type: ignore

            result = self.recursive_analysis(board, engine)

            # Undo all the moves and return the result
            board.pop()
            board.pop()

            result[0].insert(0, engine_move)
            result[0].insert(0, moves[0])
            result[2] += 1

            return result
        else:
            print('Stop due to lack of moves for engine')
            return [moves, [], 0]


    def setup_database_structure(self):
        """Create solutions table if it doesn't exist."""

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS solutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            puzzleId INTEGER UNIQUE REFERENCES puzzles(id),
            moves TEXT NOT NULL,
            length INTEGER NOT NULL,
            fish_solution TEXT NOT NULL
        );
        """
        
        index_sql = [
            "CREATE INDEX IF NOT EXISTS idx_length ON solutions (length)",
            "CREATE INDEX IF NOT EXISTS idx_puzzleId ON solutions (puzzleId)",
        ]

        self.cursor.execute(create_table_sql)
        for index_stmt in index_sql:
            self.cursor.execute(index_stmt)


    def update_database_entry(self):
        # Somehow this function is working correctly, although I don't have any idea why...
        try:
            """
            Update the whole entry in the database.
            """

            # First try to update
            update_query = """
                UPDATE solutions
                SET 
                    puzzleId = ?,
                    moves = ?,
                    length = ?,
                    fish_solution = ?
                WHERE (id = ?)
            """

            # Parameters for the update query
            update_params = (
                self.puzzleId,
                self.moves,
                self.length,
                self.fish_solution,
                self.id  # WHERE clause parameter
            )

            self.cursor.execute(update_query, update_params)

            # If no rows were updated, insert new record
            if self.cursor.rowcount == 0:
                self.insert_database_entry()

            self.connection.commit()
        except sqlite3.IntegrityError:
            print('Dupelicate entry')


    def insert_database_entry(self):
        insert_query = """
            INSERT INTO solutions (
                puzzleId,
                moves,
                length,
                fish_solution
            ) VALUES (?, ?, ?, ?)
        """

        insert_params = (
            self.puzzleId,
            self.moves,
            self.length,
            self.fish_solution,
        )

        self.cursor.execute(insert_query, insert_params)
        
        if self.cursor.rowcount == 1:
            # New row inserted - get the auto-incremented ID
            self.id = self.cursor.lastrowid
        else:
            # Row already exists - fetch the existing ID
            select_query = "SELECT id FROM solutions WHERE puzzleId = ?"
            self.cursor.execute(select_query, (self.puzzleId,))
            existing_row = self.cursor.fetchone()
            self.id = existing_row[0]

        self.connection.commit()


def get_moves(board: chess.Board) -> list[chess.Move]:
    result = []

    for move in board.legal_moves:
        result.append(move)

    return result