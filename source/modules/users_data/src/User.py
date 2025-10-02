from __future__ import annotations

import random
import sqlite3

from ...users import User
from ...puzzles import Opening
from ...database import get_connection

class User_expand(User):
    def __init__(self, id=0):
        super().__init__(id)

        self.elo = 1000.0
        self.elodev = 350.0
        self.volatility = 0.06

        self.current_puzzle = 0
        self.current_puzzle_move = 0


    def count_solved_puzzles(self):
        self.cursor.execute('''
            SELECT COUNT(*)
            FROM played
            WHERE userId = ?;
        ''', (self.id,))

        return self.cursor.fetchone()[0]


    def select_another_puzzle(self, id):
        self.current_puzzle = id
        self.current_puzzle_move = 0

        self.update_database_entry()


    def puzzle_selection_policy(self):
        # preferences = Preferences(self.ml, self.connection, searchByUserId=self.id)

        opening_ids = []

        # This weird if statements will be used with preferences
        if 0 == 1 or 0 == 0:
            opening_ids = [0]
        else:
            opening_ids = (Opening.searchById(id=0)).get_children()

        if 0 == 0:
            self.cursor.execute('''
                SELECT *
                FROM puzzles
                LEFT JOIN played ON puzzles.id = played.puzzleId AND played.userId = ?
                WHERE puzzles.isProcessed = 1
                AND played.puzzleId IS NULL
                ORDER BY MAX(ABS(puzzles.elo + puzzles.elodev/3 - ?), ABS(puzzles.elo - puzzles.elodev/3 - ?)) ASC
            ''', (self.id, self.elo + 0, self.elo + 0))
        else:
            self.cursor.execute(f'''
                SELECT *
                FROM puzzles
                LEFT JOIN played ON puzzles.id = played.puzzleId AND played.userId = ?
                WHERE puzzles.isProcessed = 1 AND puzzles.openingId IN ({','.join('?' * len(opening_ids))})
                AND played.puzzleId IS NULL
                ORDER BY MAX(ABS(puzzles.elo + puzzles.elodev/3 - ?), ABS(puzzles.elo - puzzles.elodev/3 - ?)) ASC
            ''', [self.id] + opening_ids + [self.elo + 0, self.elo + 0])
        
        p = self.cursor.fetchall()

        if len(p) == 0:
            self.select_another_puzzle(3)

            return 1

        elo = p[0][2]

        p = [a for a in p if a[2] == elo]
        
        id = random.sample(p, 1)[0][0]
        self.select_another_puzzle(id)

        return 0


    def inherit(self, user: User | User_expand):
        self.connection = user.connection
        self.cursor = user.cursor

        self.id = user.id
        self.nickname = user.nickname
        self.pgroup = user.pgroup

    
    @staticmethod
    def searchById(id: int) -> User_expand:
        user = User_expand()
        user.inherit(User().searchById(id))

        connection = get_connection()
        cursor = connection.cursor()

        if id != 0:
            cursor.execute('SELECT elo, elodev, volatility, current_puzzle, current_puzzle_move FROM user_data WHERE userId=? LIMIT 1', (id,))

            data = cursor.fetchone()

            if data is not None:
                user.elo = data[0]
                user.elodev = data[1]
                user.volatility = data[2]
                user.current_puzzle = data[3]
                user.current_puzzle_move = data[4]

            else:
                user.id = 0
                user.nickname = ''
                user.pgroup = 1000

        return user
    

    def update_database_entry(self):
        super().update_database_entry()
    
        try:
            """
            Update the whole entry in the database.
            """

            # First try to update
            update_query = """
                UPDATE user_data
                SET 
                    elo = ?,
                    elodev = ?,
                    volatility = ?,
                    current_puzzle = ?,
                    current_puzzle_move = ?
                WHERE (userId = ?)
            """

            # Parameters for the update query
            update_params = (
                self.elo,
                self.elodev,
                self.volatility,
                self.current_puzzle,
                self.current_puzzle_move,
                self.id  # WHERE clause parameter
            )

            self.cursor.execute(update_query, update_params)

            # If no rows were updated, insert new record
            if self.cursor.rowcount == 0:
                self.insert_database_entry()

            self.connection.commit()
        except sqlite3.IntegrityError:
            # print('Dupelicate entry')
            pass

    def insert_database_entry(self):
        super().insert_database_entry()

        insert_query = """
            INSERT INTO user_data (
                userId,
                elo,
                elodev,
                volatility,
                current_puzzle,
                current_puzzle_move
            ) VALUES (?, ?, ?, ?, ?, ?)
        """

        insert_params = (
            self.id,
            self.elo,
            self.elodev,
            self.volatility,
            self.current_puzzle,
            self.current_puzzle_move,
        )

        self.cursor.execute(insert_query, insert_params)

        self.connection.commit()


    @staticmethod
    def setup_database_structure():
        User.setup_database_structure()

        """Create users table if it doesn't exist."""
        
        connection = get_connection()
        cursor = connection.cursor()

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS user_data (
            id INTEGER PRIMARY KEY,
            userId INTEGER NOT NULL REFERENCES users(id),
            elo REAL DEFAULT 1000,
            elodev REAL DEFAULT 350,
            volatility REAL DEFAULT 0.06,
            current_puzzle INTEGER DEFAULT 0,
            current_puzzle_move INTEGER DEFAULT 0
        );
        """
        
        index_sql = [
        ]

        cursor.execute(create_table_sql)
        for index_stmt in index_sql:
            cursor.execute(index_stmt)

        connection.commit()

    def __repr__(self):
        return f"users.User(id={self.id}, nickname='{self.nickname}', pgroup={self.pgroup}, elo={self.elo}, elodev={self.elodev}, volatility={self.volatility}, current_puzzle={self.current_puzzle}, current_puzzle_move={self.current_puzzle_move})"
