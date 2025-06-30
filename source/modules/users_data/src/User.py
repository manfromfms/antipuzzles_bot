import sqlite3

from ...users import User
from ...database import get_connection

class User_expand(User):
    def __init__(self, id=0):
        super().__init__(id)

        self.elo = 1000
        self.elodev = 350
        self.volatility = 0.06

        self.current_puzzle = 0
        self.current_puzzle_move = 0


    def inherit(self, user: User):
        self.connection = user.connection
        self.cursor = user.cursor

        self.id = user.id
        self.nickname = user.nickname
        self.pgroup = user.pgroup

    
    @staticmethod
    def searchById(id: int) -> User:
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
                    elodev = ?
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
            elo INTEGER DEFAULT 1000,
            elodev INTEGER DEFAULT 350,
            volatility INTEGER DEFAULT 0.06,
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
