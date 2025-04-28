import sqlite3

from src.cls.Game import *
from src.cls.Opening import *
import chess

class Puzzle:
    def __init__(self, connection: sqlite3.Connection, searchById=''):
        self.connection = connection
        self.cursor = self.connection.cursor()

        self.id = 0
        self.gameId = 0
        self.elo = 1000
        self.elodev = 256
        self.fen = ''
        self.openingId = 0
        self.opening = Opening(self.connection)
        self.isProcessed = False
        self.turn = True

        self.game = Game(connection)

    def loadFromBoard(self, board: chess.Board):
        self.fen = board.fen()
        self.turn = board.turn

        self.update_database_entry()


    def update_game_parent(self, game: Game):
        self.gameId = game.id
        self.game = game

        self.update_database_entry()


    def set(self, key: str, value: any):
        setattr(self, key, value)


    def update_database_entry(self):
        # Somehow this function is working correctly, although I don't have any idea why...
        try:
            """
            Update the whole entry in the database.
            """

            # First try to update
            update_query = """
                UPDATE puzzles
                SET 
                    gameId = ?,
                    elo = ?,
                    elodev = ?,
                    fen = ?,
                    openingId = ?,
                    isProcessed = ?,
                    turn = ?
                WHERE (id = ?)
            """

            # Parameters for the update query
            update_params = (
                self.gameId,
                self.elo,
                self.elodev,
                self.fen,
                self.openingId,
                self.isProcessed,
                self.turn,
                self.id  # WHERE clause parameter
            )

            print(update_params)

            self.cursor.execute(update_query, update_params)

            # If no rows were updated, insert new record
            if self.cursor.rowcount == 0:
                self.insert_database_entry()

            self.connection.commit()
        except sqlite3.IntegrityError:
            print('Dupelicate entry')


    def insert_database_entry(self):
        insert_query = """
            INSERT INTO puzzles (
                gameId,
                elo,
                elodev,
                fen,
                openingId,
                isProcessed,
                turn
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        insert_params = (
            self.gameId,
            self.elo,
            self.elodev,
            self.fen,
            self.openingId,
            self.isProcessed,
            self.turn,
        )

        self.cursor.execute(insert_query, insert_params)
        
        if self.cursor.rowcount == 1:
            # New row inserted - get the auto-incremented ID
            self.id = self.cursor.lastrowid
        else:
            # Row already exists - fetch the existing ID
            select_query = "SELECT id FROM puzzles WHERE gameId = ?"
            self.cursor.execute(select_query, (self.gameId,))
            existing_row = self.cursor.fetchone()
            self.id = existing_row[0]

        self.connection.commit()


    def setup_database_structure(self):
        """Create puzzles table if it doesn't exist."""

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS puzzles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gameId INTEGER REFERENCES games(id),
            elo INTEGER,
            elodev INTEGER,
            fen TEXT UNIQUE,
            openingId TEXT,
            isProcessed INTEGER,
            turn INTEGER
        );
        """
        
        index_sql = [
            "CREATE INDEX IF NOT EXISTS idx_gameId ON puzzles (gameId)",
            "CREATE INDEX IF NOT EXISTS idx_turn ON puzzles (turn)",
        ]

        self.cursor.execute(create_table_sql)
        for index_stmt in index_sql:
            self.cursor.execute(index_stmt)

        self.connection.commit()

