from __future__ import annotations

import sqlite3

import src.cls.themes.theme_opening as theme_opening
import src.cls.themes.theme_middlegame as theme_middlegame
import src.cls.themes.theme_endgame as theme_endgame

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader
    from src.cls.Solution import Solution
    from src.cls.Puzzle import Puzzle

class Theme:
    def __init__(self, ml: 'ModuleLoader', connection: sqlite3.Connection, puzzle: Puzzle, solution: Solution):
        
        self.id = 0

        self.connection = connection
        self.cursor = self.connection.cursor()

        self.ml = ml

        self.puzzle = puzzle
        self.solution = solution

        self.puzzleId = puzzle.id
        self.solutionId = solution.id

        self.isValid = 1

        # Categories list (default downvotes for category is 1 so that corresponding category is rated as -1)
        # Before adding new category it has to be added to the db structure
        self.opening_upvotes = 0
        self.opening_downvotes = 1

        self.middlegame_upvotes = 0
        self.middlegame_downvotes = 1

        self.endgame_upvotes = 0
        self.endgame_downvotes = 1


    def generate(self):
        # Call all selected categories
        self.opening_upvotes, self.opening_downvotes = theme_opening.generate_category(self.puzzle, self.solution)
        self.middlegame_upvotes, self.middlegame_downvotes = theme_middlegame.generate_category(self.puzzle, self.solution)
        self.endgame_upvotes, self.endgame_downvotes = theme_endgame.generate_category(self.puzzle, self.solution)

        # Finish generation by updating the db entry
        self.update_database_entry()


    def update_database_entry(self):
        # Somehow this function is working correctly, although I don't have any idea why...
        try:
            """
            Update the whole entry in the database.
            """

            # First try to update
            update_query = """
                UPDATE themes
                SET 
                    puzzleId = ?,
                    solutionId = ?,

                    isValid = ?,
                    
                    opening_upvotes = ?,
                    opening_downvotes = ?,
                    
                    middlegame_upvotes = ?,
                    middlegame_downvotes = ?,
                    
                    endgame_upvotes = ?,
                    endgame_downvotes = ?
                WHERE id = ?
            """

            # Parameters for the update query
            update_params = (
                self.puzzleId,
                self.solutionId,

                self.isValid,   

                self.opening_upvotes,
                self.opening_downvotes,

                self.middlegame_upvotes,
                self.middlegame_downvotes,

                self.endgame_upvotes,
                self.endgame_downvotes,

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
            INSERT INTO themes (
                puzzleId,
                solutionId,

                isValid,

                opening_upvotes,
                opening_downvotes,

                middlegame_upvotes,
                middlegame_downvotes,

                endgame_upvotes,
                endgame_downvotes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        insert_params = (
            self.puzzleId,
            self.solutionId,

            self.isValid,

            self.opening_upvotes,
            self.opening_downvotes,

            self.middlegame_upvotes,
            self.middlegame_downvotes,

            self.endgame_upvotes,
            self.endgame_downvotes,
        )

        self.cursor.execute(insert_query, insert_params)
        
        if self.cursor.rowcount == 1:
            # New row inserted - get the auto-incremented ID
            self.id = self.cursor.lastrowid
        else:
            # Row already exists - fetch the existing ID
            select_query = "SELECT id FROM themes WHERE puzzleId = ?"
            self.cursor.execute(select_query, (self.puzzleId,))
            existing_row = self.cursor.fetchone()
            self.id = existing_row[0]

        self.connection.commit()


    def setup_database_structure(self):
        """Create puzzles table if it doesn't exist."""

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS themes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            puzzleId INTEGER REFERENCES puzzles(id),
            solutionId INTEGER REFERENCES solutions(id),

            isValid INTEGER DEFAULT 1,

            opening_upvotes REAL DEFAULT 0,
            opening_downvotes REAL DEFAULT 1,

            middlegame_upvotes REAL DEFAULT 0,
            middlegame_downvotes REAL DEFAULT 1,

            endgame_upvotes REAL DEFAULT 0,
            endgame_downvotes REAL DEFAULT 1
        );
        """
        
        index_sql = [
            "CREATE INDEX IF NOT EXISTS idx_categories_puzzleId ON themes (puzzleId)",
        ]

        self.cursor.execute(create_table_sql)

        self.connection.commit()

        for index_stmt in index_sql:
            self.cursor.execute(index_stmt)

        self.connection.commit()

