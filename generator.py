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

    for puzzle in tqdm(puzzles, unit='puzzle'):
        puzzle = ml.Puzzle.Puzzle(ml, connection, searchById=puzzle.id)

        if puzzle.isProcessed != 0:
            continue

        puzzle.isProcessed = -1
        puzzle.update_database_entry()

        solution = ml.Solution.Solution(ml, connection, puzzle)

        solution.generate()


def db_setup(connection: sqlite3.Connection):

    (ml.Game.Game(ml, connection)).setup_database_structure()
    (ml.Puzzle.Puzzle(ml, connection)).setup_database_structure()
    (ml.Puzzle.Puzzle(ml, connection)).setup_database_structure_positions()
    (ml.Opening.Opening(ml, connection)).setup_database_structure()
    (ml.Solution.Solution(ml, connection, ml.Puzzle.Puzzle(ml, connection))).setup_database_structure()
    (ml.Theme.Theme(ml, connection, ml.Puzzle.Puzzle(ml, connection), ml.Solution.Solution(ml, connection, ml.Puzzle.Puzzle(ml, connection)))).setup_database_structure()

    connection.commit()


# Main function
if __name__ == "__main__":
    connection = db.create_db('./puzzles.db')

    db_setup(connection)
    cursor = connection.cursor()

    # Cleanup games table (removed from the beginning for better multithread performance)
    '''print('Cleaning up games table')
    cursor.execute('DELETE FROM games WHERE id NOT IN (SELECT gameId FROM puzzles)')
    connection.commit()'''

    if len(sys.argv) > 1:
        if sys.argv[1] == 'themes':
            print('Updating themes')

            cursor.execute('SELECT id FROM themes')
            data = cursor.fetchall()

            empty_puzzle = ml.Puzzle.Puzzle(ml, connection)
            empty_solution = ml.Solution.Solution(ml, connection, empty_puzzle)

            for (id,) in tqdm(data):
                theme = ml.Theme.Theme(ml, connection, empty_puzzle, empty_solution, searchById=id)

                theme.generate()

        else:
            file_path = sys.argv[1]
            if os.path.isfile(file_path):
                print('Reading', file_path)
                positions = read_file(file_path, connection)
        
            if 'nogen' not in sys.argv:
                process_db(connection)
    else:
        if 'nogen' not in sys.argv:
            process_db(connection)

    # Cleanup games table
    print('Cleaning up games table')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM games WHERE id NOT IN (SELECT gameId FROM puzzles)')
    connection.commit()