import sqlite3

class Database:
    def __init__(self, path='database.db'):
        self.con = sqlite3.connect(path)
        self.cur = self.con.cursor()

