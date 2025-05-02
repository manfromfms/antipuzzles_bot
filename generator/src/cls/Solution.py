import sqlite3

import os
from dotenv import load_dotenv
load_dotenv()

class Solution:
    def __init__(self, connection: sqlite3.Connection):
        
        self.connection = connection
        self.cursor = connection.cursor()

        self.puzzleId = 0
        self.moves = ''
        self.fish_solution = ''

    def generate(self):
        print(os.getenv('ffish_path'))
