from __future__ import annotations

import sqlite3

import src.cls.themes.theme_opening as theme_opening
import src.cls.themes.theme_middlegame as theme_middlegame
import src.cls.themes.theme_endgame as theme_endgame
import src.cls.themes.theme_zugzwang as theme_zugzwang
import src.cls.themes.theme_cleaning as theme_cleaning

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader
    from src.cls.Solution import Solution
    from src.cls.Puzzle import Puzzle

class Theme:
    def __init__(self, ml: 'ModuleLoader', connection: sqlite3.Connection, puzzle: Puzzle, solution: Solution, searchById=0, searchByPuzzleId=0):
        
        self.id = searchById

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

        self.zugzwang_upvotes = 0
        self.zugzwang_downvotes = 1

        self.cleaning_upvotes = 0
        self.cleaning_downvotes = 1

        if searchById != 0 or searchByPuzzleId != 0:

            if searchById != 0:
                self.cursor.execute('SELECT * FROM themes WHERE id = ?', (searchById,))
            elif searchByPuzzleId != 0:
                self.cursor.execute('SELECT * FROM themes WHERE puzzleId = ?', (searchByPuzzleId,))

            data = self.cursor.fetchone()

            if data is None:
                return

            self.id = data[0]

            self.puzzleId = data[1]
            self.solutionId = data[2]

            self.puzzle = ml.Puzzle.Puzzle(self.ml, self.connection, searchById=self.puzzleId)
            self.solution = ml.Solution.Solution(self.ml, self.connection, self.puzzle, searchByPuzzleId=self.puzzleId)

            self.isValid = data[3]

            # Categories list (default downvotes for category is 1 so that corresponding category is rated as -1)
            # Before adding new category it has to be added to the db structure
            self.opening_upvotes = data[4]
            self.opening_downvotes = data[5]

            self.middlegame_upvotes = data[6]
            self.middlegame_downvotes = data[7]

            self.endgame_upvotes = data[8]
            self.endgame_downvotes = data[9]

            self.zugzwang_upvotes = data[10]
            self.zugzwang_downvotes = data[11]

            self.cleaning_upvotes = data[12]
            self.cleaning_downvotes = data[13]


    def generate(self):
        # Call all selected categories
        self.opening_upvotes, self.opening_downvotes = theme_opening.generate_category(self.puzzle, self.solution)
        self.middlegame_upvotes, self.middlegame_downvotes = theme_middlegame.generate_category(self.puzzle, self.solution)
        self.endgame_upvotes, self.endgame_downvotes = theme_endgame.generate_category(self.puzzle, self.solution)
        self.zugzwang_upvotes, self.zugzwang_downvotes = theme_zugzwang.generate_category(self.puzzle, self.solution)
        self.cleaning_upvotes, self.cleaning_downvotes = theme_cleaning.generate_category(self.puzzle, self.solution)

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
                    endgame_downvotes = ?,
                    
                    zugzwang_upvotes = ?,
                    zugzwang_downvotes = ?,
                    
                    cleaning_upvotes = ?,
                    cleaning_downvotes = ?
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

                self.zugzwang_upvotes,
                self.zugzwang_downvotes,

                self.cleaning_upvotes,
                self.cleaning_downvotes,

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
                endgame_downvotes,
                    
                zugzwang_upvotes,
                zugzwang_downvotes,
                    
                cleaning_upvotes,
                cleaning_downvotes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

            self.zugzwang_upvotes,
            self.zugzwang_downvotes,

            self.cleaning_upvotes,
            self.cleaning_downvotes,
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
            endgame_downvotes REAL DEFAULT 1,

            zugzwang_upvotes REAL DEFAULT 0,
            zugzwang_downvotes REAL DEFAULT 1,

            cleaning_upvotes REAL DEFAULT 0,
            cleaning_downvotes REAL DEFAULT 1
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

