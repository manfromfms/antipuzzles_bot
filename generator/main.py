import sys
import os

import src.games_loop as games_loop
from src.cls.Game import *
from src.cls.Puzzle import *

import src.db as db

import sqlite3

# Reads a file and returns the positions
def read_file(file_path, cursor: sqlite3.Cursor):
    positions = games_loop.loop_through_games(file_path, cursor)

    return positions


def process_db():
    print('2')


def db_setup(cursor: sqlite3.Cursor):

    (Game(cursor=cursor)).setup_database_schema()
    (Puzzle(cursor=cursor)).setup_database_schema()

    cursor.connection.commit()


# Main function
if __name__ == "__main__":
    cursor = db.create_db('../puzzles.db')

    db_setup(cursor)

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.isfile(file_path):
            positions = read_file(file_path, cursor)
        else:
            process_db()
    else:
        process_db()