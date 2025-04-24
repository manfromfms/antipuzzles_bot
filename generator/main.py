import sys
import os

import src.games_loop as games_loop
from src.cls.Game import *
from src.cls.Puzzle import *

import src.db as db

import sqlite3

# Reads a file and returns the positions
def read_file(file_path, connection: sqlite3.Connection):
    positions = games_loop.loop_through_games(file_path, connection)

    return positions


def process_db():
    print('2')


def db_setup(connection: sqlite3.Connection):

    (Game(connection=connection)).setup_database_structure()
    (Puzzle(connection=connection)).setup_database_structure()

    connection.commit()


# Main function
if __name__ == "__main__":
    connection = db.create_db('../puzzles.db')

    db_setup(connection)

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.isfile(file_path):
            positions = read_file(file_path, connection)
        else:
            process_db()
    else:
        process_db()