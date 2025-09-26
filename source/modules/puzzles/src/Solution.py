from __future__ import annotations

import sqlite3

import chess.engine
import chess.variant
from chess.engine import Mate, Cp

import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv('.env'))

from .Puzzle import Puzzle
from ...database import get_connection

class Solution:
    def __init__(self):
            
        self.connection = get_connection()
        self.cursor = self.connection.cursor()

        self.id = 0
        self.puzzleId = 0
        self.moves = ''
        self.length = 0
        self.fish_solution = ''


    def get_puzzle(self) -> Puzzle:
        return Puzzle.searchById(self.puzzleId)


    @staticmethod
    def searchById(id: int) -> Solution:
        solution = Solution()

        if id != 0:
            connection = get_connection()
            cursor = connection.cursor() # sqlite3.Cursor

            cursor.execute('SELECT * FROM solutions WHERE id = ? LIMIT 1', (id,))
            data = cursor.fetchone()

            if data is None:
                return solution
            
            solution.id = data[0]
            solution.puzzleId = data[1]
            solution.moves = data[2]
            solution.length = data[3]
            solution.fish_solution = data[4]

        return solution
    

    @staticmethod
    def searchByPuzzleId(puzzleId: int) -> Solution:
        solution = Solution()

        if puzzleId != 0:
            connection = get_connection()
            cursor = connection.cursor() # sqlite3.Cursor

            cursor.execute('SELECT * FROM solutions WHERE puzzleId = ? LIMIT 1', (puzzleId,))
            data = cursor.fetchone()

            if data is None:
                return solution
            
            solution.id = data[0]
            solution.puzzleId = data[1]
            solution.moves = data[2]
            solution.length = data[3]
            solution.fish_solution = data[4]

        return solution


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
                engine_move = engine.play(board, chess.engine.Limit(time=0.6)).move
                board.push(engine_move) # type: ignore

                result = self.recursive_analysis(board, engine)

                # Undo all the moves and return the result
                board.pop()
                board.pop()

                if len(result[0]) > 0:
                    result[0].insert(0, engine_move)
                    result[0].insert(0, moves[0])

                else:
                    result[1].insert(0, engine_move)
                    result[1].insert(0, moves[0])

                return result
            else:
                print('Stop due to lack of moves for engine')
                return [moves, [], 0]

        # Now if there are multiple legal moves
        # Do wide analysis of every possible move in current position
        wide_analysis = engine.analyse(board, chess.engine.Limit(time=2), multipv=500)

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
            result[0].insert(0, correct_move)
            result[2] += 1

            return result
        else:
            print('Stop due to lack of moves for engine')
            return [correct_move, [], 0]


    @staticmethod
    def setup_database_structure():
        """Create solutions table if it doesn't exist."""
        
        connection = get_connection()
        cursor = connection.cursor()

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

        cursor.execute(create_table_sql)
        for index_stmt in index_sql:
            cursor.execute(index_stmt)


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


    def __repr__(self):
        return (
            f"puzzles.Solution("
            f"id={self.id}, "
            f"puzzleId={self.puzzleId}, "
            f"moves='{self.moves}', "
            f"length={self.length}, "
            f"fish_solution='{self.fish_solution}'"
            f")"
        )


def get_moves(board: chess.Board) -> list[chess.Move]:
    result = []

    for move in board.legal_moves:
        result.append(move)

    return result