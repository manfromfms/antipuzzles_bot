from __future__ import annotations

import sqlite3

from .themes.theme_opening import generate_category as theme_opening
from .themes.theme_middlegame import generate_category as theme_middlegame
from .themes.theme_endgame import generate_category as theme_endgame
from .themes.theme_zugzwang import generate_category as theme_zugzwang
from .themes.theme_cleaning import generate_category as theme_cleaning
from .themes.theme_queenrace import generate_category as theme_queenrace
from .themes.theme_promotion import generate_category as theme_promotion
from .themes.theme_enpassant import generate_category as theme_enpassant

from .Puzzle import Puzzle
from .Solution import Solution
from ...database import get_connection

class Theme:
    def __init__(self):
        
        self.id = 0

        self.connection = get_connection()
        self.cursor = self.connection.cursor()

        self.puzzleId = 0
        self.solutionId = 0

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

        self.queenrace_upvotes = 0
        self.queenrace_downvotes = 1

        self.promotion_upvotes = 0
        self.promotion_downvotes = 1

        self.enpassant_upvotes = 0
        self.enpassant_downvotes = 1

    @staticmethod
    def searchById(id: int) -> Theme:
        theme = Theme()

        if id != 0:
            connection = get_connection()
            cursor = connection.cursor() # sqlite3.Cursor
            
            cursor.execute('SELECT * FROM themes WHERE id = ?', (id,))
            data = cursor.fetchone()

            if data is None:
                return theme

            theme.id = data[0]

            theme.puzzleId = data[1]
            theme.solutionId = data[2]

            theme.isValid = data[3]

            # Categories list (default downvotes for category is 1 so that corresponding category is rated as -1)
            # Before adding new category it has to be added to the db structure
            theme.opening_upvotes = data[4]
            theme.opening_downvotes = data[5]

            theme.middlegame_upvotes = data[6]
            theme.middlegame_downvotes = data[7]

            theme.endgame_upvotes = data[8]
            theme.endgame_downvotes = data[9]

            theme.zugzwang_upvotes = data[10]
            theme.zugzwang_downvotes = data[11]

            theme.cleaning_upvotes = data[12]
            theme.cleaning_downvotes = data[13]

            theme.queenrace_upvotes = data[14]
            theme.queenrace_downvotes = data[15]

            theme.promotion_upvotes = data[16]
            theme.promotion_downvotes = data[17]

            theme.enpassant_upvotes = data[18]
            theme.enpassant_downvotes = data[19]

        return theme


    @staticmethod
    def searchByPuzzleId(id):
        theme = Theme()

        if id != 0:
            connection = get_connection()
            cursor = connection.cursor() # sqlite3.Cursor

            cursor.execute('SELECT * FROM themes WHERE puzzleId = ?', (id,))

            data = cursor.fetchone()

            if data is None:
                return

            theme.id = data[0]

            theme.puzzleId = data[1]
            theme.solutionId = data[2]

            theme.isValid = data[3]

            # Categories list (default downvotes for category is 1 so that corresponding category is rated as -1)
            # Before adding new category it has to be added to the db structure
            theme.opening_upvotes = data[4]
            theme.opening_downvotes = data[5]

            theme.middlegame_upvotes = data[6]
            theme.middlegame_downvotes = data[7]

            theme.endgame_upvotes = data[8]
            theme.endgame_downvotes = data[9]

            theme.zugzwang_upvotes = data[10]
            theme.zugzwang_downvotes = data[11]

            theme.cleaning_upvotes = data[12]
            theme.cleaning_downvotes = data[13]

            theme.queenrace_upvotes = data[14]
            theme.queenrace_downvotes = data[15]

            theme.promotion_upvotes = data[16]
            theme.promotion_downvotes = data[17]

            theme.enpassant_upvotes = data[18]
            theme.enpassant_downvotes = data[19]


    def get_puzzle(self) -> Puzzle:
        return Puzzle.searchById(self.puzzleId)


    def get_solution(self) -> Solution:
        return Solution.searchById(self.solutionId)


    @staticmethod
    def generate(puzzle: Puzzle, solution: Solution) -> None:
        if puzzle.fen == '':
            print('Empty fen', puzzle.id)
            return
        
        theme = Theme()

        theme.puzzleId = puzzle.id
        theme.solutionId = solution.id

        # Call all selected categories
        theme.opening_upvotes, theme.opening_downvotes = theme_opening(puzzle, solution)
        theme.middlegame_upvotes, theme.middlegame_downvotes = theme_middlegame(puzzle, solution)
        theme.endgame_upvotes, theme.endgame_downvotes = theme_endgame(puzzle, solution)
        theme.zugzwang_upvotes, theme.zugzwang_downvotes = theme_zugzwang(puzzle, solution)
        theme.cleaning_upvotes, theme.cleaning_downvotes = theme_cleaning(puzzle, solution)
        theme.queenrace_upvotes, theme.queenrace_downvotes = theme_queenrace(puzzle, solution)
        theme.promotion_upvotes, theme.promotion_downvotes = theme_promotion(puzzle, solution)
        theme.enpassant_upvotes, theme.enpassant_downvotes = theme_enpassant(puzzle, solution)

        # Finish generation by updating the db entry
        theme.update_database_entry()


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
                    cleaning_downvotes = ?,

                    queenrace_upvotes = ?,
                    queenrace_downvotes = ?,

                    promotion_upvotes = ?,
                    promotion_downvotes = ?,

                    enpassant_upvotes = ?,
                    enpassant_downvotes = ?
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

                self.queenrace_upvotes,
                self.queenrace_downvotes,

                self.promotion_upvotes,
                self.promotion_downvotes,

                self.enpassant_upvotes,
                self.enpassant_downvotes,

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
                cleaning_downvotes,

                queenrace_upvotes,
                queenrace_downvotes,

                promotion_upvotes,
                promotion_downvotes,

                enpassant_upvotes,
                enpassant_downvotes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

            self.queenrace_upvotes,
            self.queenrace_downvotes,

            self.promotion_upvotes,
            self.promotion_downvotes,

            self.enpassant_upvotes,
            self.enpassant_downvotes,
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


    @staticmethod
    def setup_database_structure():
        """Create puzzles table if it doesn't exist."""
        
        connection = get_connection()
        cursor = connection.cursor()

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
            cleaning_downvotes REAL DEFAULT 1,

            queenrace_upvotes REAL DEFAULT 0,
            queenrace_downvotes REAL DEFAULT 1,

            promotion_upvotes REAL DEFAULT 0,
            promotion_downvotes REAL DEFAULT 1,

            enpassant_upvotes REAL DEFAULT 0,
            enpassant_downvotes REAL DEFAULT 1
        );
        """
        
        index_sql = [
            "CREATE INDEX IF NOT EXISTS idx_categories_puzzleId ON themes (puzzleId)",
        ]

        cursor.execute(create_table_sql)

        for index_stmt in index_sql:
            cursor.execute(index_stmt)

        connection.commit()

