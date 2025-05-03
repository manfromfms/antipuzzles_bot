import sys
import os

import src.games_loop as games_loop

from src.ModuleLoader import ModuleLoader
ml = ModuleLoader()

import src.db as db

import sqlite3

from tqdm import tqdm

# Reads a file and returns the positions
def read_file(file_path, connection: sqlite3.Connection):
    positions = games_loop.loop_through_games(file_path, connection)

    return positions


# Go through all unprocessed puzzels and process them
def process_db(connection: sqlite3.Connection):
    puzzles = (ml.Puzzle.Puzzle(ml, connection)).select_puzzles('SELECT id, isProcessed FROM puzzles WHERE isProcessed = 0 LIMIT 1000000')

    for puzzle in tqdm(puzzles):
        solution = ml.Solution.Solution(ml, connection, puzzle)

        solution.generate()


def db_setup(connection: sqlite3.Connection):

    (ml.Game.Game(ml, connection)).setup_database_structure()
    (ml.Puzzle.Puzzle(ml, connection)).setup_database_structure()
    (ml.Opening.Opening(ml, connection)).setup_database_structure()
    (ml.Solution.Solution(ml, connection, ml.Puzzle.Puzzle(ml, connection))).setup_database_structure()
    (ml.Category.Category(ml, connection, ml.Puzzle.Puzzle(ml, connection), ml.Solution.Solution(ml, connection, ml.Puzzle.Puzzle(ml, connection)))).setup_database_structure()

    connection.commit()


# Main function
if __name__ == "__main__":
    connection = db.create_db('./puzzles.db')

    db_setup(connection)

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.isfile(file_path):
            positions = read_file(file_path, connection)
        
        process_db(connection)
    else:
        process_db(connection)