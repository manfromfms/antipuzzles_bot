import sqlite3

import random


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader


class User:
    def __init__(self, ml: 'ModuleLoader', connection: sqlite3.Connection, id=0, searchById=0):

        self.connection = connection
        self.cursor = self.connection.cursor()

        self.ml = ml
        
        self.id = id
        self.nickname = ''
        self.elo = 1000
        self.elodev = 350
        self.volatility = 0.06
        self.pgroup = 1000
        self.current_puzzle = 0
        self.current_puzzle_move = 0

        self.cursor.execute('SELECT id FROM puzzles LIMIT 1')
        self.current_puzzle = self.cursor.fetchone()[0]

        if searchById != 0:
            self.cursor.execute('SELECT * FROM users WHERE id=? LIMIT 1', (searchById,))

            data = self.cursor.fetchone()

            if data is not None:
                self.id = data[0]
                self.nickname = data[1]
                self.elo = data[2]
                self.elodev = data[3]
                self.volatility = data[4]
                self.pgroup = data[5]
                self.current_puzzle = data[6]
                self.current_puzzle_move = data[7]


    def count_solved_puzzles(self):
        self.cursor.execute('''
            SELECT COUNT(*)
            FROM played
            WHERE userId = ?;
        ''', (self.id,))

        return self.cursor.fetchone()[0]


    def select_another_puzzle(self, id):
        self.current_puzzle = id
        self.current_puzzle_move = 0

        self.update_database_entry()


    def puzzle_selection_policy(self):
        preferences = self.ml.Preferences.Preferences(self.ml, self.connection, searchByUserId=self.id)

        self.cursor.execute('''SELECT * FROM puzzles
WHERE elo = (
    SELECT elo
    FROM (
        SELECT DISTINCT p.id, p.elo
        FROM puzzles p
        INNER JOIN solutions s ON p.id = s.puzzleId
        WHERE p.id NOT IN (
            SELECT puzzleId
            FROM played
            WHERE userId = ?
        )
        AND (s.puzzleId IS NULL OR s.puzzleId NOT IN (
            SELECT puzzleId
            FROM played
            WHERE userId = ?
        ))
    ) AS eligible_puzzles
    ORDER BY ABS(elo - ?)
    LIMIT 1
);''', (self.id, self.id, self.elo + preferences.rating_difference,))
        
        id = random.sample(self.cursor.fetchall(), 1)[0][0]
        self.select_another_puzzle(id)
        

    def update_database_entry(self):
        # Somehow this function is working correctly, although I don't have any idea why...
        try:
            """
            Update the whole entry in the database.
            """

            # First try to update
            update_query = """
                UPDATE users
                SET 
                    nickname = ?,
                    elo = ?,
                    elodev = ?,
                    volatility = ?,
                    pgroup = ?,
                    current_puzzle = ?,
                    current_puzzle_move = ?
                WHERE (id = ?)
            """

            # Parameters for the update query
            update_params = (
                self.nickname,
                self.elo,
                self.elodev,
                self.volatility,
                self.pgroup,
                self.current_puzzle,
                self.current_puzzle_move,
                self.id  # WHERE clause parameter
            )

            self.cursor.execute(update_query, update_params)

            # If no rows were updated, insert new record
            if self.cursor.rowcount == 0:
                self.insert_database_entry()

            self.connection.commit()
        except sqlite3.IntegrityError:
            # print('Dupelicate entry')
            pass


    def insert_database_entry(self):
        insert_query = """
            INSERT INTO users (
                id,
                nickname,
                elo,
                elodev,
                volatility,
                pgroup,
                current_puzzle,
                current_puzzle_move
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        insert_params = (
            self.id,
            self.nickname,
            self.elo,
            self.elodev,
            self.volatility,
            self.pgroup,
            self.current_puzzle,
            self.current_puzzle_move,
        )

        self.cursor.execute(insert_query, insert_params)

        self.connection.commit()

    
    def setup_database_structure_played(self):
        """Create played table if it doesn't exist."""

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS played (
            id INTEGER PRIMARY KEY,
            puzzleId INTEGER DEFAULT 0 REFERENCES puzzles (id),
            userId INTEGER DEFAULT 0 REFERENCES users (id),
            won INTEGER DEFAULT 0
        );
        """
        
        index_sql = [
            "CREATE INDEX IF NOT EXISTS idx_puzzleId_played ON played (puzzleId)",
            "CREATE INDEX IF NOT EXISTS idx_userId_played ON played (userId)",
        ]

        self.cursor.execute(create_table_sql)
        for index_stmt in index_sql:
            self.cursor.execute(index_stmt)

        self.connection.commit()
        


    def setup_database_structure(self):
        """Create users table if it doesn't exist."""

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            nickname TEXT NOT NULL,
            elo REAL DEFAULT 1000,
            elodev REAL DEFAULT 350,
            volatility REAL DEFAULT 0.06,
            pgroup INTEGER DEFAULT 1000,
            current_puzzle INTEGER DEFAULT 1 REFERENCES puzzles (id),
            current_puzzle_move INTEGER DEFAULT 0 NOT NULL
        );
        """
        
        index_sql = [
        ]

        self.cursor.execute(create_table_sql)
        for index_stmt in index_sql:
            self.cursor.execute(index_stmt)

        self.connection.commit()
        