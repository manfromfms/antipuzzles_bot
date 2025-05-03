from __future__ import annotations

import sqlite3
import chess.pgn

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader

class Game:
    def __init__(self, ml: 'ModuleLoader', connection: sqlite3.Connection, searchById=0, searchByGameId='') -> None:
        """
        This class stores game headers.

            [Event "Weekly Antichess Team Battle"]
            [Site "https://lichess.org/t6FYl1m6"]
            [Date "2025.04.19"]
            [White "AlwaysPlayTooSlow"]
            [Black "aleksschtin"]
            [Result "1-0"]
            [GameId "t6FYl1m6"]
            [UTCDate "2025.04.19"]
            [UTCTime "16:15:43"]
            [WhiteElo "2071"]
            [BlackElo "2414"]
            [WhiteRatingDiff "+11"]
            [BlackRatingDiff "-10"]
            [Variant "Antichess"]
            [TimeControl "90+0"]
            [ECO "?"]
            [Termination "Normal"]
            [Annotator "lichess.org"]
        """

        self.connection = connection
        self.cursor = self.connection.cursor() # sqlite3.Cursor
        self.id = 0

        self.ml = ml

        self.Event = ''
        self.Site = ''
        self.Date = ''
        self.White = ''
        self.Black = ''
        self.Result = ''
        self.GameId = ''
        self.UTCDate = ''
        self.UTCTime = ''
        self.WhiteElo = 0
        self.BlackElo = 0
        self.WhiteRatingDiff = 0
        self.BlackRatingDiff = 0
        self.Variant = ''
        self.TimeControl = ''
        self.ECO = ''
        self.Termination = ''
        self.Annotator = ''
        
        self.valid = False # Is the game loaded or not

        if searchById != 0:
            # TODO: search game by it's id in the database
            print(self.cursor.execute(f"SELECT * FROM games WHERE id = {searchById} LIMIT 1"))

        elif searchByGameId != '':
            # TODO: search game by GameId (provided by lichess)
            print(self.cursor.execute(f"SELECT * FROM games WHERE id = {searchById} LIMIT 1"))
        

    def loadFromHeaders(self, headers: chess.pgn.Headers):
        self.Event = headers['Event']
        self.Site = headers['Site']
        self.Date = headers['Date']
        self.White = headers['White']
        self.Black = headers['Black']
        self.Result = headers['Result']
        self.GameId = headers['GameId']
        self.UTCDate = headers['UTCDate']
        self.UTCTime = headers['UTCTime']
        self.WhiteElo = headers['WhiteElo']
        self.BlackElo = headers['BlackElo']
        self.WhiteRatingDiff = headers['WhiteRatingDiff']
        self.BlackRatingDiff = headers['BlackRatingDiff']
        self.Variant = headers['Variant']
        self.TimeControl = headers['TimeControl']
        self.ECO = headers['ECO']
        self.Termination = headers['Termination']
        self.Annotator = headers['Annotator']

        self.update_database_entry()


    def set(self, key: str, value: any):
        setattr(self, key, value)


    def update_database_entry(self):
        """
        Update the whole entry in the database.
        """

        # If the id is 0
        if self.id == 0:
            self.insert_database_entry()
            return

        # First try to update
        update_query = """
            UPDATE games 
            SET 
                Event = ?,
                Site = ?,
                Date = ?,
                White = ?,
                Black = ?,
                Result = ?,
                GameId = ?,
                UTCDate = ?,
                UTCTime = ?,
                WhiteElo = ?,
                BlackElo = ?,
                WhiteRatingDiff = ?,
                BlackRatingDiff = ?,
                Variant = ?,
                TimeControl = ?,
                ECO = ?,
                Termination = ?,
                Annotator = ?
            WHERE id = ?
        """

        # Parameters for the update query
        update_params = (
            self.Event,
            self.Site,
            self.Date,
            self.White,
            self.Black,
            self.Result,
            self.GameId,
            self.UTCDate,
            self.UTCTime,
            self.WhiteElo,
            self.BlackElo,
            self.WhiteRatingDiff,
            self.BlackRatingDiff,
            self.Variant,
            self.TimeControl,
            self.ECO,
            self.Termination,
            self.Annotator,
            self.id  # WHERE clause parameter
        )

        self.cursor.execute(update_query, update_params)

        # If no rows were updated, insert new record
        if self.cursor.rowcount == 0:
            self.insert_database_entry()
            return

        self.connection.commit()


    def insert_database_entry(self):
        insert_query = """
            INSERT INTO games (
                Event,
                Site,
                Date,
                White,
                Black,
                Result,
                GameId,
                UTCDate,
                UTCTime,
                WhiteElo,
                BlackElo,
                WhiteRatingDiff,
                BlackRatingDiff,
                Variant,
                TimeControl,
                ECO,
                Termination,
                Annotator
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT DO NOTHING
        """

        insert_params = (
            self.Event,
            self.Site,
            self.Date,
            self.White,
            self.Black,
            self.Result,
            self.GameId,
            self.UTCDate,
            self.UTCTime,
            self.WhiteElo,
            self.BlackElo,
            self.WhiteRatingDiff,
            self.BlackRatingDiff,
            self.Variant,
            self.TimeControl,
            self.ECO,
            self.Termination,
            self.Annotator
        )

        self.cursor.execute(insert_query, insert_params)
        
        if self.cursor.rowcount == 1:
            # New row was inserted
            self.id = self.cursor.lastrowid
        else:
            # Row already exists, fetch the existing ID
            select_query = "SELECT id FROM games WHERE GameId = ?"
            self.cursor.execute(select_query, (self.GameId,))
            existing_row = self.cursor.fetchone()
            self.id = existing_row[0]

        self.connection.commit()


    def setup_database_structure(self) -> None:
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY,
                Event TEXT,
                Site TEXT,
                Date TEXT,
                White TEXT,
                Black TEXT,
                Result TEXT,
                GameId TEXT UNIQUE,
                UTCDate TEXT,
                UTCTime TEXT,
                WhiteElo INTEGER,
                BlackElo INTEGER,
                WhiteRatingDiff INTEGER,
                BlackRatingDiff INTEGER,
                Variant TEXT,
                TimeControl TEXT,
                ECO TEXT,
                Termination TEXT,
                Annotator TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_games_white 
            ON games (White)
        ''')

        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_games_black 
            ON games (Black)
        ''')

        self.connection.commit()
