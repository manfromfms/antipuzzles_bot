from __future__ import annotations

import sqlite3
import chess.pgn

from ...database import get_connection

class Game:
    """This class stores game headers.

    An example of stored data:

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

    def __init__(self) -> None:
        self.connection = get_connection()
        self.cursor = self.connection.cursor() # sqlite3.Cursor
        self.id: int = 0

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

    
    @staticmethod
    def searchById(id: int) -> Game:
        connection = get_connection()
        cursor = connection.cursor() # sqlite3.Cursor

        game = Game()

        if id != 0:
            cursor.execute(f"SELECT * FROM games WHERE id = {id} LIMIT 1")
            data = cursor.fetchone()

            game.id = data[0]
            game.Event = data[1]
            game.Site = data[2]
            game.Date = data[3]
            game.White = data[4]
            game.Black = data[5]
            game.Result = data[6]
            game.GameId = data[7]
            game.UTCDate = data[8]
            game.UTCTime = data[9]
            game.WhiteElo = data[10]
            game.BlackElo = data[11]
            game.WhiteRatingDiff = data[12]
            game.BlackRatingDiff = data[13]
            game.Variant = data[14]
            game.TimeControl = data[15]
            game.ECO = data[16]
            game.Termination = data[17]
            game.Annotator = data[18]

        return game
        

    def loadFromHeaders(self, headers: chess.pgn.Headers):
        """Make another game entry in the database based off chess game headers.

        Args:
            headers (chess.pgn.Headers): Game headers.
        """
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


    def set(self, key: str, value):
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
            self.id = self.cursor.lastrowid # type: ignore
        else:
            # Row already exists, fetch the existing ID
            select_query = "SELECT id FROM games WHERE GameId = ?"
            self.cursor.execute(select_query, (self.GameId,))
            existing_row = self.cursor.fetchone()
            self.id = existing_row[0]

        self.connection.commit()


    @staticmethod
    def setup_database_structure() -> None:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute('''
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

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_games_white 
            ON games (White)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_games_black 
            ON games (Black)
        ''')

        connection.commit()


    def __repr__(self):
        return (
            f"puzzles.Game("
            f"id={self.id}, "
            f"Event='{self.Event}', "
            f"Site='{self.Site}', "
            f"Date='{self.Date}', "
            f"White='{self.White}', "
            f"Black='{self.Black}', "
            f"Result='{self.Result}', "
            f"GameId='{self.GameId}', "
            f"UTCDate='{self.UTCDate}', "
            f"UTCTime='{self.UTCTime}', "
            f"WhiteElo={self.WhiteElo}, "
            f"BlackElo={self.BlackElo}, "
            f"WhiteRatingDiff={self.WhiteRatingDiff}, "
            f"BlackRatingDiff={self.BlackRatingDiff}, "
            f"Variant='{self.Variant}', "
            f"TimeControl='{self.TimeControl}', "
            f"ECO='{self.ECO}', "
            f"Termination='{self.Termination}', "
            f"Annotator='{self.Annotator}'"
            f")"
        )