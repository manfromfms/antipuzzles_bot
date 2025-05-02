import sqlite3

from src.cls.Puzzle import *

import os
from dotenv import load_dotenv
load_dotenv()

class Solution:
    def __init__(self, connection: sqlite3.Connection, puzzle: Puzzle, searchById=''):
        
        self.connection = connection
        self.cursor = connection.cursor()

        self.puzzleId = 0
        self.moves = ''
        self.length = 0
        self.fish_solution = ''

    def generate(self):
        print(os.getenv('ffish_path'))
