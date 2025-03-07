import sqlite3

class Database:
    def __init__(self, path='database.db'):
        self.con = sqlite3.connect(path)
        self.cur = self.con.cursor()


    def init_puzzles(self):
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS Puzzles (
                id INTEGER PRIMARY KEY,
                Site TEXT,
                WhiteElo INTEGER,
                BlackElo INTEGER,
                White TEXT,
                Black TEXT,
                TimeControl TEXT,
                fen TEXT NOT NULL,
                movesBefore TEXT,
                movesPuzzle TEXT NOT NULL,
                movesAfter TEXT
            )
        ''')

        self.con.commit()
