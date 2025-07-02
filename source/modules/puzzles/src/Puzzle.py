from __future__ import annotations

from .Game import Game
from ...database import get_connection
from .Opening import Opening

import chess
import sqlite3

class Puzzle:
    def __init__(self):
        self.connection = get_connection()
        self.cursor = self.connection.cursor()

        self.id = 0
        self.gameId: int = 0
        self.elo = 1000.0
        self.elodev = 350.0
        self.volatility = 0.06
        self.fen = ''
        self.openingId = 0
        self.isProcessed = False
        self.turn = True
        self.moveTime = 0


    @staticmethod
    def searchById(id: int) -> Puzzle:
        connection = get_connection()
        cursor = connection.cursor() # sqlite3.Cursor

        puzzle = Puzzle()

        if id != 0:
            cursor.execute('SELECT * FROM puzzles WHERE id = ? LIMIT 1', (id,))
            data = cursor.fetchone()

            if data is None:
                return puzzle
            
            puzzle.id = data[0]
            puzzle.gameId = data[1]
            puzzle.elo = data[2]
            puzzle.elodev = data[3]
            puzzle.volatility = data[4]
            puzzle.fen = data[5]
            puzzle.openingId = data[6]
            puzzle.isProcessed = data[7]
            puzzle.turn = data[8]
            puzzle.moveTime = data[9]

        return puzzle


    def loadFromBoard(self, board: chess.Board):
        self.fen = board.fen()
        self.turn = board.turn

        self.update_database_entry()


    def update_game_parent(self, game: Game):
        self.gameId = game.id
        self.game = game

        self.update_database_entry()


    def load_game(self) -> Game:
        self.game = Game.searchById(id=self.gameId)

        return self.game


    def set(self, key: str, value):
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
                    volatility = ?,
                    fen = ?,
                    openingId = ?,
                    isProcessed = ?,
                    turn = ?,
                    moveTime = ?
                WHERE (id = ?)
            """

            # Parameters for the update query
            update_params = (
                self.gameId,
                self.elo,
                self.elodev,
                self.volatility,
                self.fen,
                self.openingId,
                self.isProcessed,
                self.turn,
                self.moveTime,
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
            INSERT INTO puzzles (
                gameId,
                elo,
                elodev,
                volatility,
                fen,
                openingId,
                isProcessed,
                turn,
                moveTime
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        insert_params = (
            self.gameId,
            self.elo,
            self.elodev,
            self.volatility,
            self.fen,
            self.openingId,
            self.isProcessed,
            self.turn,
            self.moveTime
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


    @staticmethod
    def setup_database_structure():
        """Create puzzles table if it doesn't exist."""
        
        connection = get_connection()
        cursor = connection.cursor()

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS puzzles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gameId INTEGER REFERENCES games(id),
            elo REAL DEFAULT 1000,
            elodev REAL DEFAULT 350,
            volatility REAL DEFAULT 0.06,
            fen TEXT UNIQUE NOT NULL,
            openingId INTEGER REFERENCES openings(id),
            isProcessed INTEGER,
            turn INTEGER,
            moveTime INTEGER
        );
        """
        
        index_sql = [
            "CREATE INDEX IF NOT EXISTS idx_gameId ON puzzles (gameId)",
            "CREATE INDEX IF NOT EXISTS idx_turn ON puzzles (turn)",
            "CREATE INDEX IF NOT EXISTS idx_puzzles_elo ON puzzles (elo)",
        ]

        cursor.execute(create_table_sql)
        for index_stmt in index_sql:
            cursor.execute(index_stmt)

        connection.commit()


    @staticmethod
    def setup_database_structure_positions():
        """Create positions table if it doesn't exist."""
        connection = get_connection()
        cursor = connection.cursor()


        create_table_sql = """
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fen TEXT NOT NULL UNIQUE
        );
        """
        
        index_sql = [
            "CREATE INDEX IF NOT EXISTS idx_gameId ON positions (fen)",
        ]

        cursor.execute(create_table_sql)
        for index_stmt in index_sql:
            cursor.execute(index_stmt)

        connection.commit()


    @staticmethod
    def setup_database_structure_telegramImageId():
        """Create telegramImageId table if it doesn't exist."""
        connection = get_connection()
        cursor = connection.cursor()        

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS telegramImageId (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fen TEXT NOT NULL UNIQUE,
            file_id TEXT NOT NULL UNIQUE
        );
        """
        
        index_sql = [
            "CREATE INDEX IF NOT EXISTS idx_telegramImageId_fen ON telegramImageId (fen)",
        ]

        cursor.execute(create_table_sql)
        for index_stmt in index_sql:
            cursor.execute(index_stmt)

        connection.commit()


    def select_puzzles(self, query='', params=()) -> list[Puzzle]:
        self.cursor.execute(query, params)

        l = self.cursor.fetchall()

        puzzles = []

        for p in l:
            puzzles.append(Puzzle.searchById(id=p[0]))

        return puzzles
    

    def __repr__(self):
        return f"puzzles.Puzzle(id={self.id}, gameId={self.gameId}, elo={self.elo}, elodev={self.elodev}, volatility={self.volatility}, fen='{self.fen}', openingId={self.openingId}, isProcessed={self.isProcessed}, turn={self.turn}, moveTime={self.moveTime})"
    
    def getOpening(self):
        return Opening.searchById(self.openingId)
